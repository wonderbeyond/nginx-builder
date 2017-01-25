#!/usr/bin/python
# coding=utf-8

import urllib2
import os
import logging
import tarfile
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

BASE_DIR = os.path.dirname(__file__)
CONF_DIR = os.path.join(BASE_DIR, 'conf')
BUNDLE_DIR = os.path.join(BASE_DIR, 'bundle')

if not os.path.isdir(BUNDLE_DIR):
    os.makedirs(BUNDLE_DIR)


def download(url):
    logger.info('Start download %s', url)
    resp = urllib2.urlopen(url)

    content_disp = resp.info().get('Content-Disposition')

    if content_disp:
        file_name = content_disp.split('filename=')[1].strip('\'\" ')
    else:
        file_name = os.path.basename(url)

    ball_path = os.path.join(BUNDLE_DIR, file_name)

    if os.path.exists(ball_path):
        logger.warning('%s exists, not saved', ball_path)
    else:
        with open(ball_path, 'wb') as f:
            f.write(resp.read())
            logger.info('Saved as %s', ball_path)

    return ball_path


def main():
    from contextlib import closing

    class DownloadStatus(object):
        download_status_file = os.path.join(BASE_DIR, 'download-status.json')

        def __init__(self):
            try:
                self.items = json.load(open(self.download_status_file))
            except IOError:
                self.items = {}

        def set_done(self, item):
            name = item['name']
            item['status'] = 'done'
            self.items[name] = item
            self.save()

        def is_done(self, item):
            name = item['name']
            return self.items.get(name, {}).get('status') == 'done'

        def save(self):
            json.dump(self.items,
                      open(self.download_status_file, 'w'),
                      indent=4)

    download_status = DownloadStatus()

    modules_cfg_file = os.path.join(CONF_DIR, 'required-modules.json')
    pkgs_cfg_file = os.path.join(CONF_DIR, 'required-pkgs.json')

    modules = json.load(open(modules_cfg_file))
    pkgs = json.load(open(pkgs_cfg_file))

    for m in modules:
        if not download_status.is_done(m):
            ball_path = download(m['url'])
        else:
            ball_path = download_status.items[m['name']]['ball_path']
            logger.info('Skip downloading %s', m['url'])

        logger.info('Extracting %s', ball_path)
        with closing(tarfile.open(ball_path)) as tf:
            tf.extractall(path=BUNDLE_DIR)
            m['ball_path'] = ball_path
            m['path'] = tf.getmembers()[0].name
            m['type'] = 'nginx-module'
            download_status.set_done(m)
            logger.info('Done extracting')
    else:
        with open(os.path.join(BASE_DIR, 'added-modules.txt'), 'w') as f:
            for m in modules:
                name = m['name']
                f.write(download_status.items[name]['path'] + '\n')

    for pkg in pkgs:
        if not download_status.is_done(pkg):
            ball_path = download(pkg['url'])
        else:
            ball_path = download_status.items[pkg['name']]['ball_path']
            logger.info('Skip downloading %s', pkg['url'])

        logger.info('Extracting %s', ball_path)
        with closing(tarfile.open(ball_path)) as tf:
            pkg['ball_path'] = ball_path
            pkg['path'] = tf.getnames()[0]
            tf.extractall(path=BUNDLE_DIR)
            download_status.set_done(pkg)
            logger.info('Done extracting')

    download_status.save()

if __name__ == '__main__':
    main()
