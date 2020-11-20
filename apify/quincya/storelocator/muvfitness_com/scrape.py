import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    base_link = "https://www.muvfitness.com/locations/?CallAjax=GetLocations"

    session = SgRequests()
    stores = session.post(base_link, headers = HEADERS).json()

    data = []
    locator_domain = "muvfitness_com"

    for store in stores:
        location_name = store["FranchiseLocationName"]
        street_address = (store["Address1"] + " " + store["Address2"]).strip()
        city = store['City']
        state = store["State"]
        zip_code = store["ZipCode"]
        country_code = "US"
        store_number = store["FranchiseLocationID"]
        location_type = "<MISSING>"
        phone = store['Phone']
        latitude = store['Latitude']
        longitude = store['Longitude']
        link = "https://www.muvfitness.com" + store['Path']

        found = []
        hours_of_operation = ""
        hours = store['LocationHours'].split("[")[1:]
        for row in hours:
            days = row.split(":")[1].split('"')[1]
            if days in found:
                continue
            found.append(days)
            if "1" in row.split("Closed")[1][:5]:
                time = "Closed"
            else:
                time = row.split("OpenTime")[1].split(':"')[1].split(",")[0][:-1] + "-" + row.split("CloseTime")[1].split(':"')[1].split(",")[0][:-1]
            hours_of_operation = (hours_of_operation + " " + days + " " + time).strip()
        if not hours_of_operation:
            req = session.get(link, headers = HEADERS)
            base = BeautifulSoup(req.text,"lxml")
            hours_of_operation = " ".join(list(base.find(class_="gym-hours").stripped_strings)).split("Hours")[1].strip()
            if "mon" not in hours_of_operation.lower():
                hours_of_operation = "<INACCESSIBLE>"
        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
