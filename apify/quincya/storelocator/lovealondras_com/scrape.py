import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_link = "https://www.lovealondras.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    raw_data = base.find(class_="js-react-on-rails-component").contents[0]
    js = raw_data.split('locations":')[-1].split(',"menus')[0]
    store_data = json.loads(js)

    items = base.find(class_="pm-location-search-list").find_all("section")

    data = []
    for i, item in enumerate(items):
        locator_domain = "lovealondras.com"
        location_name = item.h4.text
        street_address = item.p.span.text.replace("\xa0", " ").strip()
        city_line = list(item.p.a.stripped_strings)[-1].split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = store_data[i]["id"]
        location_type = "<MISSING>"
        phone = item.find_all("p")[1].text.strip()
        hours_of_operation = " ".join(list(item.find(class_="hours").stripped_strings))
        latitude = store_data[i]["lat"]
        longitude = store_data[i]["lng"]
        link = (
            "https://www.lovealondras.com" + item.find("a", string="View Menu")["href"]
        )
        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
