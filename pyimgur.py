#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests

CLIENT_ID = os.getenv('IMGUR_CLIENT_ID', '')
CLIENT_SECRET = os.getenv('IMGUR_CLIENT_SECRET', '')
IMG_UPLOAD_API = 'https://api.imgur.com/3/upload'
ALBUM_CREATION_API = 'https://api.imgur.com/3/album'
AUTH_HEADER = {"Authorization": "Client-ID " + CLIENT_ID}
HTTP_SUCCESS_CODE = [200, 201]


def error(message, err=None):
    ''' Return error message '''
    print "{}".format(message)
    if err:
        print "More detail: {}".format(err)
    sys.exit(1)


def check_file(images):
    ''' Check if input is file and accessible '''
    for image in images:
        if not os.path.isfile(image):
            error("{} is not a file".format(image))
        elif not os.access(image, os.R_OK):
            error("{} is not accessible".format(image))
        else:
            continue


def read_file(path):
    ''' Read image and return file object '''
    try:
        with open(path, 'rb') as f:
            return f.read()
    except IOError as e:
        error("Unable to read {}".format(path), e)
    except:
        raise


def create_album():
    ''' Create album and return api endpoint and album id '''
    album_obj = requests.post(ALBUM_CREATION_API, headers=AUTH_HEADER)
    if album_obj.status_code in HTTP_SUCCESS_CODE:
        album_json = json.loads(album_obj.text)
        deletehash = album_json.get('data').get('deletehash')
        album_id = album_json.get('data').get('id')
    album_add_api = 'https://api.imgur.com/3/album/' + deletehash + '/add'
    return album_add_api, album_id


def update_album(img_ids):
    ''' Add image id into album '''
    api_endpoint, album_id = create_album()
    payload = {'ids': '%s' % ','.join(img_ids)}
    req = requests.put(api_endpoint,
                       data=payload,
                       headers=AUTH_HEADER)
    if req.status_code in HTTP_SUCCESS_CODE:
        return album_id
    else:
        return False


def upload(images):
    ''' Update one or many images and return url'''
    img_ids = []
    for image in images:
        payload = {'key': CLIENT_SECRET,
                   'image': read_file(image)}
        try:
            req = requests.post(IMG_UPLOAD_API,
                                data=payload,
                                headers=AUTH_HEADER)
            if req.status_code not in HTTP_SUCCESS_CODE:
                error("Unexpected response: {}".format(req.status_code))
            req_json = json.loads(req.text)
            img_ids.append(req_json.get('data').get('id'))
        except requests.RequestException as e:
            error("Error when connecting to imgur.com", e)
        except:
            raise
    if len(images) > 1:
        album_id = update_album(img_ids)
        url = 'https://imgur.com/a/' + album_id
    else:
        url = req_json.get('data').get('link')
    return url


def main():
    ''' Main function '''
    if not CLIENT_ID or not CLIENT_SECRET:
        print """
CLIENT_ID or CLIENT_SECRET missing.
Export keys on your terminal first:
$ export IMGUR_CLIENT_ID='your_client_id'
$ export IMGUR_CLIENT_SECRET='your_secret_key'
        """
        sys.exit(1)
    try:
        check_file(sys.argv[1:])
        if len(sys.argv) >= 2:
            print upload(sys.argv[1:])
        else:
            error("Usage: python pyimgur.py /path/to/images")
    except KeyboardInterrupt:
        error("OK, quit")

if __name__ == '__main__':
    main()
