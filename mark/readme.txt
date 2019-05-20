To get started first ensure all packages are installed. 
To run the crawler, simply type: npm run marriott (if the crawl is for Marriott hotels).

Additionally, there are various settings which can be changed.
To change any default settings go search for the config.json file.

Example:

{
    "General_Settings": {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        "headless": false,
        "delayTime": 10000,
        "headerRow": "locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, naics_code, latitude, longitude, hours_of_operation\n",
        "filenamePrefix": "../data/"
    }, 
    "Website_Settings": {
        "Marriott": {
            "filenameBody": "marriott"
        }
    }
    
}

Notes:

Headless is currently set to "false". This forces a chrome browser to pop up to ensure the crawler is working properly, but to disable this, simply set to "true".

DelayTime (in ms): Sets the amount of delay for the website being scraped/crawled. Greater than 5000 (5 seconds) is preferred due to server sending back over load errors or blacklisting you. 

