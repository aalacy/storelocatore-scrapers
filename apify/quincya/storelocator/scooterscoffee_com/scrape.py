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

    session = SgRequests()

    data = []
    locator_domain = "scooterscoffee.com"

    for i in range(1,400):
        base_link = "https://code.metalocator.com/index.php?option=com_locator&view=location&tmpl=component&task=load&framed=1&sample_data=undefined&format=json&Itemid=12991&templ[]=item_address_template&lang=&_opt_out=1&_urlparams=&distance=NaN&id=" + str(i)
        store = session.get(base_link, headers = HEADERS).json()[0]

        try:
            store_number = store["id"]
        except:
            break
        location_name = store["name"]
        if "COMING SOON" in location_name.upper() or "permanently closed" in location_name.lower():
            continue
        try:
            street_address = (store["address"] + " " + store["address2"]).strip()
        except:
            street_address = store["address"]

        if not street_address:
            street_address = "<MISSING>"

        if len(street_address) < 2:
            street_address = "<MISSING>"

        city = store['city']
        state = store["state"].replace("wav","VA")
        zip_code = store["postalcode"]
        country_code = "US"
        location_type = "<MISSING>"
        phone = store['phone']
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = store['hours'].replace("{","").replace("}"," ").replace("|"," ").strip()
        latitude = store['lat']
        longitude = store['lng']
        # link = "https://www.scooterscoffee.com/stores/" + store['slug']
        link = "<MISSING>"

        if "temporarily closed" in location_name.lower():
            hours_of_operation = "Temporarily Closed"

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
