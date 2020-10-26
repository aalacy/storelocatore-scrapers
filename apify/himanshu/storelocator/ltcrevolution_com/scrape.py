import csv
from sgrequests import SgRequests
import json
# from datetime import datetime
# import phonenumbers
from bs4 import BeautifulSoup
import re
import unicodedata
# import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ltcrevolution_com')




session = SgRequests()

def write_output(data):
    with open('data.csv',newline="", mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = "https://www.ltcrevolution.com/"
    addresses = []
    country_code = "US"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    r = session.get("https://www.ltcrevolution.com/find-a-facility/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    script = json.loads(soup.find("script",text=re.compile("google_map_data")).text.split("var MSWObject = ")[1].split("};")[0]+"}".strip())
    json_data = json.loads(script["google_map_data"])
    for x in json_data:
        location_name = x["location_name"]
        if "Primary Location" != location_name:
            location_name = location_name
            store_number = x["location_id"]
            latitude = x["lat"]
            longitude = x["lng"]
            if "street_address_line_2" in x:
                street_address = x["street_address_line_1"]+" "+x["street_address_line_2"]
            else:
                street_address = x["street_address_line_1"]
            city = x["city"]
            state = x["state_region"]
            zipp = x["zip_postal_code"]
            if "HomeNow" in location_name:
                page_url = "https://www.ltcrevolution.com/find-a-facility/shc-home-health"+location_name.split("HomeNow –")[1].lower().replace(" ","-").strip()
            else:
                page_url = "https://www.ltcrevolution.com/find-a-facility/"+location_name.lower().replace(" & ","-").replace(".","").replace(" ","-").strip()
            if "Signature HealthCARE of Savannah" == location_name.strip():
                page_url = "https://www.ltcrevolution.com/find-a-facility/signature-healthcare-rehab-of-savannah/"
            if "signature-healthcare-of-madison" in page_url.split("/")[-1]:
                page_url = "https://www.ltcrevolution.com/find-a-facility/madison-rehab-and-nursing-center/"
            if "Signature HealthCARE at Parkwood" == location_name.strip():
                page_url = "https://www.ltcrevolution.com/find-a-facility/signature-healthcare-of-parkwood"
            r1 = session.get(page_url,headers=headers)
            soup1 = BeautifulSoup(r1.text,"lxml")
            if soup1.find("span",text = re.compile("Phone: ")):
                phone = soup1.find("span",text = re.compile("Phone: ")).find_next("a").text
                
            else:
                phone = "<MISSING>"
            
            try:
                hours_of_operation = " ".join(list(soup1.find("section",class_="location-single__office-hours").stripped_strings)).replace("Office Hours",'').strip()
                
            except:
                hours_of_operation   = "<MISSING>"
            location_type = "<MISSING>"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


       


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
