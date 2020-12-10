import csv
import time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("maverik_com")

session = SgRequests()
headers = {
    
'authority': 'gateway.maverik.com',
'method': 'GET',
'path': '/ac-loc/location/all',
'scheme':'https',
'accept': 'application/json, text/plain, */*',
'accept-encoding':'gzip, deflate, br',
'accept-language': 'en-US,en;q=0.9',
'app-id': 'PAYX',
'origin': 'https://loyalty.maverik.com',
'referer': 'https://loyalty.maverik.com/',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-site',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'

}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
       data = []
       url = "https://gateway.maverik.com/ac-loc/location/all"
       loclist = session.get(url, headers=headers)#.json()["locations"]
       print(loclist.text)



fetch_data()
