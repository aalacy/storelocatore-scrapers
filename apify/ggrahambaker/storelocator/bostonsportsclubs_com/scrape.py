import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    locator_domain = "https://www.bostonsportsclubs.com/"
    ext = "clubs"
    r = session.get(locator_domain + ext, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    locs = soup.find(id="map-club-accordion").find_all(
        "li", {"class": "club-tile club-detail"}
    )

    geo_data = []
    all_scripts = soup.find_all("script")
    for script in all_scripts:
        if "var clubs =" in str(script):
            script = str(script)
            js = json.loads(script.split("=")[1].split(";\n\n")[0])
            for j in js:
                geo_data.append([j["slug"], j["latitude"], j["longitude"]])
            break

    all_store_data = []
    for loc in locs:
        link = locator_domain[:-1] + loc.find("a")["href"]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        location_name = loc.h4.text.strip()
        street_address = soup.find("span", {"itemprop": "streetAddress"}).text.strip()
        city = soup.find("span", {"itemprop": "addressLocality"}).text.strip()
        state = soup.find("span", {"itemprop": "addressRegion"}).text.strip()

        if state == "":
            state = "<MISSING>"

        zip_code = soup.find("span", {"itemprop": "postalCode"}).text.strip()

        phone_number = soup.find("span", {"itemprop": "telephone"}).text.strip()
        hours = " ".join(list(loc.table.stripped_strings))

        country_code = "US"
        store_number = loc["data-code"]
        location_type = "<MISSING>"
        lat = "<MISSING>"
        longit = "<MISSING>"

        for row in geo_data:
            if row[0] in link:
                lat = row[1]
                longit = row[2]

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
            link,
        ]

        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
