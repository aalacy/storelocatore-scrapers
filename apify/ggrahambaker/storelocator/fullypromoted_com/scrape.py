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


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def addy_ext_can(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1] + " " + state_zip[2]
    return city, state, zip_code


def fetch_data():
    locator_domain = "https://fullypromoted.com"
    ext = "/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    found = []
    all_store_data = []

    locs = base.find_all(class_="py-4 brdr-b1 brdr-c-grey")

    for loc in locs:
        content = list(loc.stripped_strings)

        location_name = "Fully Promoted " + content[0]
        phone_number = content[-1].strip()
        try:
            street_address = " ".join(content[1:-2])
            city, state, zip_code = addy_ext(content[-2])
        except:
            pass

        if "http" in loc.a["href"]:
            link = loc.a["href"].replace("/locations/htt", "htt")
        else:
            link = locator_domain + loc.a["href"]

        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            loc_j = (
                base.find_all("script", attrs={"type": "application/ld+json"})[-1]
                .contents[0]
                .replace("\n", "")
                .strip()
            )

            loc_json = json.loads(loc_j)

            lat = loc_json["geo"]["latitude"]
            longit = loc_json["geo"]["longitude"]

            if (lat + longit) in found:
                continue
            found.append(lat + longit)

            try:
                content = list(base.find(class_="pt-2 pb-4 px-4").stripped_strings)
            except:
                content = list(base.find(class_="col-md-7 col-lg-4").stripped_strings)

            location_name = content[0]
            street_address = content[1]
            city, state, zip_code = addy_ext(content[2])
            phone_number = content[3].replace("Call us:", "").strip()

            try:
                hours = " ".join(list(base.find("table").stripped_strings))
            except:
                hours = "<MISSING>"
        except:
            lat = "<MISSING>"
            longit = "<MISSING>"
            hours = "<MISSING>"
            link = locator_domain + ext

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        store_data = [
            locator_domain,
            link,
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
        ]
        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
