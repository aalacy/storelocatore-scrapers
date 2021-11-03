import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    base_url = "http://cleatswings.com"
    r = session.get("https://www.cleatswings.com/contact", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []

    items = soup.find(id="dm_content").div.find_all(class_="dmRespRow", recursive=False)
    for location in items:
        try:
            name = location.h2.text.replace("\n", " ")
        except:
            continue

        raw_address = location.a.text.split(",")
        street_address = " ".join(raw_address[:-2]).strip()
        city = raw_address[-2].strip()
        state = raw_address[-1].strip()[:-6].strip()
        zip_code = raw_address[-1][-6:].strip()

        phone = location.find("a", {"type": "call"}).text
        hours = " ".join(list(location.find(class_="open-hours-data").stripped_strings))

        map_link = location.iframe["src"]
        lat_pos = map_link.rfind("!3d")
        latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
        lng_pos = map_link.find("!2d")
        longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()

        store = []
        store.append(base_url)
        store.append(name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zip_code)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append("https://www.cleatswings.com/contact")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
