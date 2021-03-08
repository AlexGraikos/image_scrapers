import os
import glob
import json
import argparse
import PIL.Image

# Read image list from results.json file
parser = argparse.ArgumentParser(description='Parse results.json file')
parser.add_argument('file_path', help='Path to results.json')
args = parser.parse_args()

with open(args.file_path) as infile:
    results = json.load(infile)
dirname = os.path.dirname(args.file_path)

# Iterate over all images
nGeolocated = 0
nImages = 0
for img in results:

    # Count images with geolocation data
    #print('[*] Parsing', img['id'])

    latitude = float(img['latitude'])
    longitude = float(img['longitude'])
    accuracy = float(img['accuracy'])
    if latitude != 0 or longitude != 0:
        nGeolocated += 1
        print('[*] Image', img['id'],
              'has geolocation tag (lat:{:f}, long{:f}) accuracy: {:f}'.format(
              latitude, longitude, accuracy))

    # Open image
    try:
        img_path = glob.glob(os.path.join(dirname, img['id']) + '*')[0]
        img = PIL.Image.open(img_path)
        nImages += 1
    except Exception as e:
        print('[!] Could not open image:', e)

print('[*] Out of', nImages, 'images, found', nGeolocated, 'with GPS metadata')

