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

    locator_domain = "https://www.wirelessworld.com"
    ext = "/locations/"

    r = session.get(locator_domain + ext, headers=headers)

    soup = BeautifulSoup(r.content, "html.parser")

    locs = soup.find_all("h4", {"class": "city-title"})

    all_store_data = []
    for loc in locs:

        page_url = locator_domain + loc.find("a")["href"]
        r = session.get(page_url, headers=headers)

        soup = BeautifulSoup(r.content, "html.parser")

        loc_info = soup.find_all("script", {"type": "application/ld+json"})
        for script in loc_info:
            loc_json = json.loads(script.text)

            if loc_json["@type"] == "BreadcrumbList":
                continue

            hours_ul = soup.find("li", {"class": "active-day"}).parent.find_all("li")
            hours = ""
            for li in hours_ul:
                hours += li.text + " "

            location_name = loc_json["name"].replace("&#39;", "'")
            if "telephone" in loc_json:
                phone_number = loc_json["telephone"].replace("+1", "")
            else:
                phone_number = "<MISSING>"

            addy = loc_json["address"]

            street_address = addy["streetAddress"]
            city = addy["addressLocality"]
            state = addy["addressRegion"]
            zip_code = addy["postalCode"]

            country_code = "US"

            try:
                coords = loc_json["geo"]
                lat = coords["latitude"]
                longit = coords["longitude"]
            except:
                lat = "<MISSING>"
                longit = "<MISSING>"

            store_number = page_url.split("/")[4]
            location_type = "<MISSING>"

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
