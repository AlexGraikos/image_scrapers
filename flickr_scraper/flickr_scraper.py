# Generated by Glenn Jocher (glenn.jocher@ultralytics.com) for https://github.com/ultralytics
# Modified by Alexandros Graikos

import argparse
import os
import time
import json
from flickrapi import FlickrAPI
from utils.general import download_uri
import PIL.Image
import PIL.ExifTags

# Add missing tags to PIL
# https://www.exiv2.org/tags.html
# https://developer.android.com/reference/android/media/ExifInterface
PIL.ExifTags.TAGS[36880] = 'OffsetTime'
PIL.ExifTags.TAGS[36881] = 'OffsetTimeOriginal'
PIL.ExifTags.TAGS[36882] = 'OffsetTimeDigitized'
PIL.ExifTags.TAGS[34864] = 'SensitivityType'
PIL.ExifTags.TAGS[34866] = 'RecommendedExposureIndex'
PIL.ExifTags.TAGS[59932] = 'Padding'
PIL.ExifTags.TAGS[59933] = 'OffsetSchema'

key = ''  # Flickr API key
secret = ''

def get_gps_exif(img_path):
    longitude = 0
    latitude = 0
    accuracy = 0
    GPSLatRef = 'N'
    GPSLongRef = 'E'

    # Load image
    try:
        img = PIL.Image.open(img_path)
    except Exception as e:
        print('[!]', e)
        return (latitude, longitude, accuracy)

    # Extract exif GPS metadata
    exif_data = img._getexif()
    if exif_data is None:
        return (latitude, longitude, accuracy)

    for key, value in exif_data.items():
        # Translate keys to tags
        try:
            tag_name = PIL.ExifTags.TAGS[key]
        except KeyError as e:
            print('[!] Tag not found:', key)

        # If non-empty GPSInfo tag is found then print GPS data
        if tag_name == 'GPSInfo' and len(value) > 0:

            for gps_key, gps_value in value.items():
                gps_tag_name = PIL.ExifTags.GPSTAGS[gps_key]
                #print(gps_tag_name, gps_value)

                # Convert longitude/latitude to decimal degrees
                if gps_tag_name == 'GPSLatitude':
                    latitude = (float(gps_value[0]) + float(gps_value[1]) / 60 
                                + float(gps_value[2]) / 60**2)
                if gps_tag_name == 'GPSLongitude':
                    longitude = (float(gps_value[0]) + float(gps_value[1]) / 60 
                                + float(gps_value[2]) / 60**2)

                # Store lat/long reference
                if gps_tag_name == 'GPSLatitudeRef':
                    GPSLatRef = value
                if gps_tag_name == 'GPSLongitudeRef':
                    GPSLongRef = value

                # Store gps accuracy
                if gps_tag_name == 'GPSDOP':
                    accuracy = gps_value

    # Flip if referenced by S or W
    if GPSLatRef == 'S':
        latitude *= -1
    if GPSLongRef == 'W':
        longitude *= -1

    return (latitude, longitude, accuracy)


def get_urls(search='', tags='', n=-1):
    # Perform query to API
    print('[*] Querying for', search, '-', tags)
    t = time.time()
    flickr = FlickrAPI(key, secret)
    license = ()
    extras = 'description,media,realname,url_o,o_dims,geo,tags,machine_tags,date_taken'
    photos = flickr.walk(text=search,
                         tags=tags,
                         tag_mode='any',
                         extras=extras,
                         per_page=500,
                         license=license,
                         sort='relevance')
    
    # Create save directory
    savedir = (os.getcwd() + os.sep + 'images' + os.sep 
               + (search + '-' + tags).replace(' ', '_') + os.sep)
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    # Metadata for each image downloaded
    metadata = []

    urls = []
    nImages = 0
    nGPSMetadata = 0
    for i, photo in enumerate(photos):

        if (i >= n and n > 0):
            break

        try:
            # construct url https://www.flickr.com/services/api/misc.urls.html
            url = photo.get('url_o')  # original size
            if url is None:
                url = 'https://farm%s.staticflickr.com/%s/%s_%s_b.jpg' % \
                      (photo.get('farm'), photo.get('server'), photo.get('id'), photo.get('secret'))  # large size

            # download
            download_uri(url, savedir)
            nImages += 1
            
            # Get image properties
            photo_id = photo.get('id')
            title = photo.get('title')
            description = photo.find('description').text
            tags = photo.get('tags')
            latitude = float(photo.get('latitude'))
            longitude = float(photo.get('longitude'))
            accuracy = float(photo.get('accuracy'))
            date_taken = photo.get('datetaken')

            # Check if Flickr provided GPS metadata
            if (latitude != 0 or longitude != 0):
                nGPSMetadata += 1
                print('[*] Found GPS metadata from Flickr')
            else:
                # Extract GPS metadata from EXIF
                img_path = os.path.join(savedir, url.split('/')[-1])
                latitude, longitude, accuracy = get_gps_exif(img_path)

                if (latitude != 0 or longitude != 0):
                    print('[*] Found GPS metadata in exif')
                    nGPSMetadata += 1

            # Store in dict and append to metadata array
            metadata_dict = {}
            metadata_dict['id'] = photo_id
            metadata_dict['title'] = title
            metadata_dict['description'] = description 
            metadata_dict['tags'] = tags
            metadata_dict['latitude'] = latitude 
            metadata_dict['longitude'] = longitude
            metadata_dict['accuracy'] = accuracy
            metadata_dict['date_taken'] = date_taken
            metadata.append(metadata_dict)

            urls.append(url)
            print('%g/%g %s' % (i + 1, n, url))
        except Exception as e:
            print('%g/%g error...' % (i + 1, n), e)

    # Save metadata
    with open(os.path.join(savedir, 'results.json'), 'w') as outfile:
        json.dump(metadata, outfile)

    # urls = pd.Series(urls)
    # urls.to_csv(search + "_urls.csv")
    print('Out of', nImages, 'images,', nGPSMetadata, 'have GPS metadata')
    print('Done. (%.1fs)' % (time.time() - t) + 
          ('\nAll images saved to %s' % savedir))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--search', type=str, default='', 
                        help='Flickr search term')
    parser.add_argument('--tags', type=str, default='', 
                        help='flickr tags')
    parser.add_argument('--n', type=int, default=-1,
                        help='number of images')
    opt = parser.parse_args()

    # Check key
    help_url = 'https://www.flickr.com/services/apps/create/apply'
    assert key and secret, '''Flickr API key required in flickr_scraper.py L11-12. 
                              To apply visit {help_url}'''

    get_urls(search=opt.search, # search term
             tags=opt.tags, # search tags
             n=opt.n) # max number of images

