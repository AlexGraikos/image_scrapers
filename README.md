# Introduction
The Flickr image scaper is adopted from https://github.com/ultralytics/flickr_scraper.

# Requirements
Python 3.7 or later with the packages specifield in `requirements.txt`.

# Run
## Flickr
1. Request a Flickr API key: https://www.flickr.com/services/apps/create/apply
2. Write your API key and secret in `flickr_scraper.py` L11-L12:
```python
key = ''
secret = ''
```
3. Run the Flickr scraper tool as
```bash
python flickr_scraper.py --search 'search_term' --tags 'comma,separated,tags' --n nImages
```
Note that image downloads may be subject to Flickr rate limits and other limitations. See https://www.flickr.com/services/developer/api/ for full information. Results are saved in the `images` directory.

## Parsing Results
Use the `parse_results.py` script as
```bash
python parse_results.py path/to/results.json
```
to get the total number and latitudes-longitudes of geotagged images.

