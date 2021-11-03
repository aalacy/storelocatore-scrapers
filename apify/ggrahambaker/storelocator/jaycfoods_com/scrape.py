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


def fetch_data():
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    locator_domain = "https://www.jaycfoods.com/"
    ext = "storelocator-sitemap.xml"
    r = session.get(locator_domain + ext, headers=headers)

    soup = BeautifulSoup(r.content, "html.parser")
    loc_urls = soup.find_all("loc")

    link_list = []
    for loc in loc_urls:
        if "/search" in loc.text:
            continue
        link_list.append(loc.text)

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        loc_json = json.loads(
            str(soup.find("script", {"type": "application/ld+json"}))
            .split(">")[1]
            .split("<")[0]
        )

        try:
            addy = loc_json["address"]
            street_address = addy["streetAddress"]
            city = addy["addressLocality"]
            state = addy["addressRegion"]
            zip_code = addy["postalCode"]
        except:
            raw_address = (
                soup.find(class_="StoreAddress-storeAddressGuts")
                .get_text(" ")
                .replace(",", "")
                .replace(" .", ".")
                .replace("..", ".")
                .split("  ")
            )
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].strip()
            zip_code = raw_address[3].split("Get")[0].strip()

        coords = loc_json["geo"]

        lat = coords["latitude"]
        longit = coords["longitude"]

        location_name = soup.find("h1", {"class": "StoreDetails-header"}).text

        phone_number = soup.find("span", {"class": "PhoneNumber-phone"}).text
        hours = " ".join(loc_json["openingHours"])
        country_code = "US"
        page_url = link

        location_type = "<MISSING>"
        store_number = page_url.split("/")[-1]

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
            page_url,
        ]

        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
