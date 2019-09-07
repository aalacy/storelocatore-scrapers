## Marriott crawler

### Setup and dependency installation

1. The crawler is written in nodejs+apify+puppeteer. The latest version can be found and installed [here](https://nodejs.org/en/).

2. To install packages, cd into the directory containing this readme and run `npm install`.

### Usage

To run the crawler, execute `apify run`.

This crawler looks for the following environment variables:

1. `APIFY_LOCAL_STORAGE_DIR`. Used to store apify data. Default: `apify_storage`.

2. `csv`. File name to store final csv output. Default: `marriott.csv`.

Environment variables are optional and can be set as follows: `APIFY_LOCAL_STORAGE_DIR=./test_storage csv=test_storage.csv apify run`.

### Caching

The crawler will cache data when possible. It will cache both the request queue and the hotel location data. This makes it safe to quit the program and start it back up without losing data. As long as all of the location urls were crawled, this will start the crawler up where it left off. To start over, use a new local storage or delete the old one.
