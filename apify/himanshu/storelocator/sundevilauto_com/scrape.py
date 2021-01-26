import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_url = "https://www.sundevilauto.com/wp-content/uploads/json/stores.json?ver=0.5.6.1563220104"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    k = json.loads(soup.text.replace("var sda_stores = ", ""))
    for i in k:
        addresses = []
        time = ""
        name = i["title"]
        st = i["store_address_1"]
        city = i["store_city"]
        state = i["store_state"]
        zip1 = i["store_zip"]
        h1 = i["store_hours"]
        lat = i["store_lat"]
        log = i["store_long"]
        store_no = i["store_number"]
        phone = i["store_phone_number"]
        try:
            for h in h1:
                time = (time + h["day_of_week"] + " " + h["operating_hours"]).replace(
                    "Thursday: 7am-6pmMonday 7am-6pm", "Thursday: 7am-6pm"
                )
        except:
            time = "<MISSING>"
        try:
            page_url = "https://www.sundevilauto.com" + i["link"]
        except:
            page_url = "<MISSING>"
        if "1932 N. Power Rd." in st:
            time = "Monday 7am-6pm Tuesday 7am-6pm Wednesday 7am-6pm Thursday 7am-6pm Friday 7am-6pm Saturday 7:30am-5pm Sunday Closed "
        store = []
        store.append("https://www.sundevilauto.com")
        store.append(name if name else "<MISSING>")
        store.append(st if st else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip1 if zip1 else "<MISSING>")
        store.append("US")
        store.append(store_no if store_no else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("sundevilauto")
        store.append(lat if lat else "<MISSING>")
        store.append(log if log else "<MISSING>")
        store.append(time if time.strip() else "<MISSING>")
        store.append(page_url if page_url.strip() else "<MISSING>")
        store = [
            x.replace("é", "e")
            .replace("Tuesday", " Tuesday:")
            .replace("Wednesday", " Wednesday:")
            .replace("Thursday", " Thursday:")
            .replace("Friday", " Friday:")
            .replace("Saturday", " Saturday:")
            .replace(" Closed", "")
            .replace("Sunday", " Sunday: Closed")
            .replace("Saturday:  Sunday", "Saturday: Closed Sunday")
            if isinstance(x, str)
            else x
            for x in store
        ]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
