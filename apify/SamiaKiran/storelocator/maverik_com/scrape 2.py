import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
logger = SgLogSetup().get_logger("tacocabana_com")

session = SgRequests()
headers = {
'authority': 'api.koala.fuzzhq.com',
'method': 'GET',
'path': '/v1/ordering/store-locations/?include[]=operating_hours&include[]=attributes&per_page=50',
'scheme': 'https',
'accept':'*/*',
'accept-encoding':'gzip, deflate, br',
'accept-language':'en-US,en;q=0.9',
'authorization':'Bearer JkvKjTn6VWeSDzOiu3Ihyq8gm58G8DeehvI5ao7x',
'content-type':'application/json',
'origin':'https://www.tacocabana.com',
'referer':'https://www.tacocabana.com/locations',
'sec-fetch-dest':'empty',
'sec-fetch-mode':'cors',
'sec-fetch-site':'cross-site',
'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'}


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
    final_data = []
    url = "https://api.koala.fuzzhq.com/v1/ordering/store-locations/?include%5B0%5D=operating_hours&include%5B1%5D=attributes&per_page=50&page=1"
    r = session.get(url, headers=headers, verify=False)
    soup = json.loads(r.text)
    data_list = soup['data']
    print(data_list)
    #TYPE CODE TO GET DATA


def scrape():
    data = fetch_data()
    write_output(data)


fetch_data()
