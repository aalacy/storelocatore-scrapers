import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


# helper for getting address
def addy_extractor(src):
    arr = src.split(",")
    city = arr[0]
    prov_zip = arr[1].split(" ")
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]

    return city, state, zip_code


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.pioneersupermarkets.com/"

    ext = "locations/"
    to_scrape = locator_domain + ext

    page = session.get(to_scrape, headers=headers)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, "html.parser")

    all_scripts = soup.find_all("script")
    for script in all_scripts:
        if "var locations" in str(script):
            script = str(script)
            break

    js = script.split("locations =")[1].split(";\n")[0]
    stores_js = json.loads(js)

    stores = soup.find_all("li", {"class": "locator-store-item"})

    all_store_data = []

    for store in stores:
        street_address = store.find("span", {"class": "locator-address"}).text
        location_name = store.find("h4", {"class": "locator-store-name"}).text
        addy_info = (
            store.find("span", {"class": "locator-storeinformation"})
            .find("br")
            .previousSibling
        )
        city, state, zip_code = addy_extractor(addy_info)
        phone_number = store.find("a", {"class": "locator-phonenumber"}).text

        hours_html = store.find("span", {"class": "locator-storehours"})
        if hours_html is None:
            hours = "<MISSING>"
        else:
            hours = ""
            hours_split = hours_html.text.split("\n")
            for hou in hours_split:
                hours += hou + " "
            hours = hours.strip()

        country_code = "US"
        store_number = store["data-store"]
        location_type = "<MISSING>"
        lat = "<INACCESSIBLE>"
        longit = "<INACCESSIBLE>"

        for js in stores_js:
            if js["storeID"] == store_number:
                lat = js["latitude"]
                longit = js["longitude"]
                break

        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            to_scrape,
        ]
        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
