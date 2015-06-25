from datetime import datetime
from os import environ
from os.path import expanduser
import json
import time 

import flickrapi

home = expanduser("~")

flickr_key = environ['FLICKR_API_KEY']
flickr_secret = environ['FLICKR_SECRET']

def main():

    flickr = flickrapi.FlickrAPI(flickr_key, flickr_secret, format='json')

    (token, frob) = flickr.get_token_part_one(perms='write')

    if not token:
        raw_input("Press ENTER after you authorized this program")
        token = flickr.get_token_part_two((token, frob))

    all_photos = []

    print '-----> Fetching all photos'

    total_pages = 1
    page = 1
    while page <= total_pages:
        print '       Fetching page {} out of {}'.format(page, total_pages)
        res = json.loads(flickr.photos_search(user_id='me', page=page, per_page=500, extras='date_upload,date_taken')[14:-1])
        total_pages = res['photos']['pages']
        page = res['photos']['page'] + 1
        photos = res['photos']['photo']
        all_photos.extend(photos)

    print '-----> Updating dates'

    for photo in  all_photos:
        date_taken = photo['datetaken']
        date_taken = datetime.strptime(date_taken, '%Y-%m-%d %H:%M:%S') #convert date taken to a string
        date_posted = int(photo['dateupload'])
        date_posted = datetime.fromtimestamp(date_posted) #import date uploaded as a date time
        if date_posted != date_taken:
            print '       Updating "{}": change date posted from {} to {}'.format(photo['id'], date_posted, date_taken)
            new_date_posted = time.mktime(date_taken.timetuple()) #convert to seconds since the unix epoch                   #datetime.strftime(date_taken, '%Y-%m-%d %H:%M:%S')
	    try:
                flickr.photos_setDates(photo_id=photo['id'], date_posted=new_date_posted) 
            except flickrError as fuck_you:
                fuck_you=sys.exec_info()[0]
		print "I done fucked up."
		print fuck_you
	    print new_date_posted
        else:
            print '       Skipping "{}": dates match'.format(photo['id'])
    print '-----> Done!'

if __name__ == "__main__":
    main()
