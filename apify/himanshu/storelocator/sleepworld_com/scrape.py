import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    }

    base_url = "https://www.sleepworld.com/"
    api = "https://www.sleepworld.com/amlocator/index/ajax/"
    json_data = session.get(api, headers=headers).json()

    for d in json_data["items"]:
        locator_domain = base_url
        location_name = d["name"]
        street_address = d["address"]
        city = d["city"]
        state = "CA"
        zipp = d["zip"]
        country_code = d["country"]
        store_number = d["id"]
        phone = d["phone"]
        location_type = "Mattress Store"
        latitude = d["lat"]
        longitude = d["lng"]
        page_url = "https://www.sleepworld.com/locations/" + d["url_key"]
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        hours = []
        hho = soup.find("div", {"class": "amlocator-schedule-table"}).find_all(
            "div", {"class": "amlocator-row"}
        )
        for h in hho:
            day = h.find("span", {"class": "amlocator-cell -day"}).text
            time = h.find("span", {"class": "amlocator-cell -time"}).text
            frame = day + " " + time
            hours.append(frame)

        hours_of_operation = ",".join(hours)

        store = []
        store.append(locator_domain)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)

        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
