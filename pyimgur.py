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


def imgur_conn_error(err):
    ''' Handle error of connecting to imgur.com '''
    print "Error while contacting with imgur.com!"
    print "{}".format(err)
    sys.exit(1)


def imgur_http_error(err):
    ''' Handle HTTP error response from imgur.com '''
    print "HTTP return code: {}".format(err)
    sys.exit(1)


def upload_image(img, in_album=False):
    ''' Return uploaded data info in dictionary '''
    try:
        with open(img, 'rb') as f:
            payload = {
                'key': CLIENT_SECRET,
                'image': f.read()
            }
        req = requests.post(IMG_UPLOAD_API, data=payload, headers=AUTH_HEADER)
        if req.status_code in HTTP_SUCCESS_CODE:
            req_json = json.loads(req.text)
            if not in_album:
                return req_json['data']['link']
            else:
                return req_json
        else:
            print "Upload image failed!"
            imgur_http_error(req.status_code)
    except requests.RequestException as e:
        imgur_conn_error(e)
    except IOError:
        print "Unable to open {}".format(img)
        sys.exit(1)
    except:
        raise


def upload_album(imgs):
    ''' Upload multiple files into one album, return album url '''
    try:
        # Create album first
        create_album = requests.post(ALBUM_CREATION_API, headers=AUTH_HEADER)
        if create_album.status_code in HTTP_SUCCESS_CODE:
            album_json = json.loads(create_album.text)
            deletehash = album_json['data']['deletehash']
            album_id = album_json['data']['id']
            album_add_api = 'https://api.imgur.com/3/album/' + deletehash + \
                '/add'
            img_ids = []
            for img in imgs:
                img_data = upload_image(img, in_album=True)
                img_ids.append(str(img_data['data']['id']))
            payload = {
                'ids': '%s' % ','.join(img_ids)
            }
        else:
            print "Album creation failed!"
            imgur_http_error(create_album.status_code)
        # Update images to album and return album url
        update_album = requests.put(album_add_api,
                                    data=payload,
                                    headers=AUTH_HEADER)
        if update_album.status_code in HTTP_SUCCESS_CODE:
            return 'https://imgur.com/a/' + album_id
        else:
            print "Updating images to album failed!"
            imgur_http_error(update_album.status_code)
    except requests.RequestException as e:
        imgur_conn_error(e)
    except:
        raise


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
    if len(sys.argv) >= 3:
        print upload_album(sys.argv[1:])
    elif len(sys.argv) == 2:
        print upload_image(sys.argv[1])
    else:
        print "Usage: python pyimgur.py /path/to/images"
        sys.exit(1)

if __name__ == '__main__':
    main()
