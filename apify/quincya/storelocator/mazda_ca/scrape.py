import csv
from sgrequests import SgRequests


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    base_link = "https://www.mazda.ca/api/dealersearch/query/keywords?searchTerm=%&page=0&limit=200&lang=en&serviceType=sales%2Cservice%2Cparts"

    session = SgRequests()
    stores = session.get(base_link, headers = HEADERS).json()

    data = []
    locator_domain = "mazda.ca"

    for store in stores:
        store = store["Dealer"]
        location_name = store["DealerName"].encode("ascii", "replace").decode().replace("?","e")
        street_address = (store["Address"][0]["Address1"] + " " + store["Address"][0]["Address2"]).strip().encode("ascii", "replace").decode().replace("?","e")
        city = store["Address"][0]['City'].encode("ascii", "replace").decode().replace("?","e")
        state = store["Address"][0]["Region"]
        zip_code = store["Address"][0]["Zip"]
        country_code = "CA"
        store_number = store["DealerId"]
        location_type = "<MISSING>"
        phone = store["Contact"][0]['PhoneNumber']
        latitude = store["Address"][0]['Latitude']
        longitude = store["Address"][0]['Longitude']
        link = store["Contact"][0]['WebsiteUrl']

        hour_types = store["OpeningTimes"]
        for row in hour_types:
            if row["ServiceType"] == "Sales":
                break
        hours_of_operation = ""
        raw_hours = row["Days"]
        for raw_hour in raw_hours:
            hours_of_operation = hours_of_operation + raw_hour["Day"] + " " + raw_hour["OpenTime"] + "-" + raw_hour["CloseTime"] + " "

        hours_of_operation = hours_of_operation.replace("Closed-Closed","Closed").strip()

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
