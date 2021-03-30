import csv
import time
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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


def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url, headers=headers, data=data)
                else:
                    r = session.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://st-regis.marriott.com/"
    location_url = "https://pacsys.marriott.com/data/marriott_properties_WI_en-US.json"
    r = session.get(location_url, headers=headers).json()
    k = r["regions"]
    for i in k:
        canada = i["region_countries"]
        for i1 in canada:
            ab = i1["country_states"]
            for i2 in ab:
                bc = i2["state_cities"]
                for i3 in bc:
                    cd = i3["city_properties"]
                    for i4 in cd:
                        location_name = i4["name"].replace("é", "e")
                        street_address = i4["address"]
                        state = i4["state_name"]
                        city = i4["city"]
                        zipp = i4["postal_code"]
                        country_code = i4["country_code"]
                        phone = i4["phone"]
                        latitude = i4["latitude"]
                        longitude = i4["longitude"]
                        link_data = i4["marsha_code"]
                        page_url = "https://www.marriott.com/hotels/travel/" + str(
                            link_data
                        )
                        store = []
                        store.append(base_url if base_url else "<MISSING>")
                        store.append(location_name if location_name else "<MISSING>")
                        store.append(street_address if street_address else "<MISSING>")
                        store.append(city if city else "<MISSING>")
                        store.append(state if state else "<MISSING>")
                        store.append(zipp if zipp else "<MISSING>")
                        store.append(country_code if country_code else "<MISSING>")
                        store.append("<MISSING>")
                        store.append(phone if phone else "<MISSING>")
                        store.append("Westin Hotels & Resorts")
                        store.append(latitude if latitude else "<MISSING>")
                        store.append(longitude if longitude else "<MISSING>")
                        store.append("<MISSING>")
                        store.append(page_url if page_url else "<MISSING>")
                        if country_code == "US" or country_code == "CA":
                            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
