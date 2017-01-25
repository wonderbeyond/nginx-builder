#!/usr/bin/python
# coding=utf-8
import argparse
import os
import json

BASE_DIR = os.path.realpath(os.path.dirname(__file__))
BUNDLE_DIR = os.path.join(BASE_DIR, 'bundle')
download_status_file = os.path.join(BASE_DIR, 'download-status.json')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('module_info', nargs='?', default='')
    parser.add_argument('--show-path', action='store_true', dest='show_path')
    
    args = parser.parse_args()
    modules = json.load(open(download_status_file))
    m = modules.get(args.module_info)

    if args.show_path:
        print os.path.join(BUNDLE_DIR, m['path'])
