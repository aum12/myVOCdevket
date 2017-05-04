#!/usr/bin/env python
import argparse
import os
import shutil
import sys
import random

def create_dir(directory):
    """Create a directory and remove it if it exists"""
    if os.path.exists(directory):
        conf_prompt('Directory {} exists.\nDo you want to replace it?'.format(directory))
        shutil.rmtree(directory)
    os.makedirs(directory)
    print 'Created Directory: {}\n'.format(directory)

def copy_imgs(id_list, source, target):
    """Copy images from source to target directories based on annotation list"""
    create_dir(target)
    img_list = ['{}.jpg'.format(name) for name in id_list]
    print 'Copying images from \n{}\nto\n{}\n'.format(source, target)
    for i, fname in enumerate(img_list):
        if i % 10 == 0:
            print 'copying {}'.format(fname)
        shutil.copy2(os.path.join(source, fname), os.path.join(target, fname))
    print '\nCopy Complete.'

def get_idlist(anno_dir):
    """Create list of all xml annotation files in directory"""
    id_list = [os.path.splitext(f)[0] for f in os.listdir(anno_dir) if f.endswith('.xml')]
    id_list = sorted(id_list)  # sort list by name (acend)
    return id_list

def write_to_file(l, fname):
    with open(fname, 'wt') as f:
        f.write('\n'.join(l))
    print 'File Saved: {}'.format(fname)


def create_data_splits(id_list, split_percent):
    """Split data id list into trainval / test ids. Split ids are saved to file."""
    random.shuffle(id_list)

    split_ix = int(len(id_list) * split_percent)  # floor to int
    write_to_file(id_list[:split_ix], 'trainval.txt')
    write_to_file(id_list[split_ix:], 'test.txt')

def read_id_file(fname):
    with open(fname) as f:
        id_list = [i.strip() for i in f.readlines()]
    return id_list

def conf_prompt(question):
    """ Prompts for user input / confirmation. Always exits script on 'no' entry."""
    yes = set(['yes', 'y', 'ye'])
    no = set(['no', 'n'])
    while True:
        print question + ' [y/n].'
        choice = raw_input('input> ').lower()
        if choice in yes:
            print   # blank line
            return
        elif choice in no:
            print 'Exiting. Good Bye.'
            sys.exit(1)
        else:
            sys.stdout.write("Please respond with 'yes' or 'no'.\n")

def do_split_data(args):
    """Entry function to split training data"""
    # setup absolute paths with current directory
    cur_dir = os.getcwd()
    anno_source = os.path.join(cur_dir, args.anno_dir)
    print 'Annotation Dir: {}\nTrainval/Test Split: {} / {}'.format(anno_source, args.dsplit, 1-args.dsplit)
    conf_prompt('Ready to create data lists using the following parameters. Proceed?')

    id_list = get_idlist(anno_source)
    create_data_splits(id_list, args.dsplit)

def do_cpimgs(args):
    """Entry function to copy images based on annoatation image file names"""
    # setup absolute paths with current directory
    cur_dir = os.getcwd()
    anno_source = os.path.join(cur_dir, args.anno_dir)
    img_target = os.path.join(cur_dir, args.target_dir)
    img_source = args.img_dir

    print 'Annotations Dir: {}\nSource Image Dir: {}\nTarget Image Dir: {}\n'.format(anno_source, img_source, img_target)
    conf_prompt('Ready to copy images using these parameters. Proceed?')
    #create image id list and copy corresponding images to target dir
    id_list = get_idlist(anno_source)
    copy_imgs(id_list, img_source, img_target)
    write_to_file(id_list, 'ids.txt')

def do_join_idlists(args):
    """Entry function to concat image/annotation id lists"""
    print 'Files to join:'
    for f in args.id_files: print f
    print '\nTarget file: {}\n'.format(os.path.join(os.getcwd(), args.fname))
    conf_prompt('Ready to join files using these parameters. Proceed?')

    all_ids = [read_id_file(f) for f in args.id_files]
    uniq_ids = list(set().union(*all_ids))
    random.shuffle(uniq_ids)
    write_to_file(uniq_ids, args.fname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data munging utilities for PASCAL VOC formatted datasets')
    subparsers = parser.add_subparsers()

    cmd_parser = subparsers.add_parser('cpAnnoImgs', help='Copy image files corresponding to file names in Annotation directory')
    cmd_parser.add_argument('img_dir', help='Absolute path to source image directory to copy from (.jpg files)')
    cmd_parser.add_argument('-a', '--annodir', dest='anno_dir', default='Annotations',
            help='Source annotation directory containing all annotation files')
    cmd_parser.add_argument('-t', '--targetdir', dest='target_dir', default='JPEGImages',
            help='Target images directory containing the matching annotation files')
    cmd_parser.set_defaults(func=do_cpimgs)

    cmd_parser = subparsers.add_parser('splitData', help='Create shuffled trainval / test data splits')
    cmd_parser.add_argument('-a', '--annodir', dest='anno_dir', default='Annotations',
            help='Source annotation directory containing all annotation files')
    cmd_parser.add_argument('-s', '--trainsplit', dest='dsplit', type=float, default=0.8,
            help='Percentage of dataset to include in train/val data set (float). Remaining will go to test.')
    cmd_parser.set_defaults(func=do_split_data)

    cmd_parser = subparsers.add_parser('joinDataLists', help='Concatenate id lists and shuffle')
    cmd_parser.add_argument('id_files', nargs='+', help='set of data id list files (absolute path to files)')
    cmd_parser.add_argument('-f', '--fname', dest='fname', default='join_trainval.txt',
            help='Source annotation directory containing all annotation files')
    cmd_parser.set_defaults(func=do_join_idlists)

    # get arguments
    args = parser.parse_args()
    if args.func is None:
        parser.print_help()
        sys.exit(1)
    else:
        args.func(args)
