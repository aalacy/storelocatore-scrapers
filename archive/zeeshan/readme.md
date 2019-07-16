Install Dependencies
--------------------
``` 
pip install -r requirements.txt
```

Run Crawlers
------------
```
python CRAWLER_NAME.py # e.g. python marriott.py
```

Reverse Geocoding
-----------------
Some crawlers (e.g. MAC) require reverse geocoding of addresses to make up a searchable query. We are using Google Geocoding API to that end. <br />
In order to run these crawlers, please create Geocoding Enabled API Key and add it to environment variable `GOOGLE_API_KEY`. 

Notes
-----
 - `base.py` has a base class that provides fundamental components shared by each crawler
 - All programs were developed using python 2.7

