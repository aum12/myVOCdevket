#!/usr/bin/env python

import cv2
import os
import sys
import fnmatch
import argparse

def grab_files(path):
    """Recursively get the filenames and paths of all video files in root directory (passed as param)"""
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.avi'):
            matches.append((os.path.splitext(filename)[0], os.path.join(root, filename)))
    return matches

def create_dir(directory):
    """Create a directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def grab_frames(files, save_root, rate=5):
    """Extract frames from video file and save images to disk"""
    for video in files:
        cap = cv2.VideoCapture(video[1])
        print 'Getting images from %s' % video[1]
        frame_no = 0
        file_no = 0
        save_dir = create_dir(os.path.join(save_root, video[0]))
        print save_dir
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret is True:
                if frame_no % rate == 0:
                    save_img = '{}_{:06d}.{}'.format(video[0], file_no, 'jpg')
                    cv2.imwrite(os.path.join(save_dir, save_img), frame)
                    file_no += 1
                if frame_no % 50 == 0:
                    print 'Writing: %s' % save_img
                frame_no += 1
            else:
                cap.release()
                print 'Completed: %s' % video[1]

def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(description='Arguments for Video frame extraction')
    parser.add_argument('source', help='relative source directory of video files')
    parser.add_argument('target', help='relative target directory to store extract image files')
    parser.add_argument('--frate', dest='frate', type=int, default=12, help='how many video frames to skip before extracting an image')

    return parser.parse_args()

if __name__ == '__main__':
    #get arguments
    args = parse_args()
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(cur_dir, args.source)
    target_path = os.path.join(cur_dir, args.target)
    files = grab_files(data_path)
    print 'data path: %s' % data_path
    print 'target path: %s' % target_path
    print files
    grab_frames(files, target_path, args.frate)
