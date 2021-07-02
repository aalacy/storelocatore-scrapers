import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def addy_extractor(state_city):
    city = state_city.split(",")[0]
    state_zip = state_city.split(",")[1].strip().split(" ")
    if len(state_zip) == 2:
        state = state_zip[0]
        zip_code = state_zip[1][0:3] + " " + state_zip[1][3:]
    else:
        state = state_zip[0]
        zip_code = state_zip[1] + " " + state_zip[2]

    return city.strip(), state.strip(), zip_code.strip()


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
    locator_domain = "https://www.firehousesubs.ca/"
    ext = "all-locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locs = base.find(class_="locations_wrap").find_all("article")

    link_list = []
    for loc in locs:
        cont = loc.text.strip().split("\n")
        phone_number = cont[-1]
        add = loc.address
        link = loc.a["href"]
        if "Coming Soon" in cont[0]:
            continue

        link_list.append([link, phone_number, cont[0], add])

    all_store_data = []
    for cont in link_list:
        link = "https://www.firehousesubs.ca" + cont[0]
        phone_number = cont[1]

        req = session.get(link, headers=headers)
        if req.status_code == 200:
            got_page = True
        else:
            got_page = False

        name_and_number = cont[2].split("#")
        store_number = name_and_number[1].strip()
        location_name = name_and_number[0].strip()
        country_code = "CA"
        location_type = "<MISSING>"
        hours = "<MISSING>"
        page_url = "https://www.firehousesubs.ca/all-locations/"
        lat = "<MISSING>"
        longit = "<MISSING>"

        if got_page:
            base = BeautifulSoup(req.text, "lxml")
            div_info = (
                base.address.text.replace(" \r", "")
                .replace("\r", "")
                .strip()
                .split("\n")
            )
            street_address = " ".join(div_info[:-1]).strip()
            city, state, zip_code = addy_extractor(
                div_info[-1].strip().replace("  ", " ")
            )
            page_url = link
            hours = " ".join(list(base.find(class_="hours").ol.stripped_strings))

            map_str = base.find(class_="map_wrap").img["src"]
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[0].split(
                ","
            )
            lat = geo[0]
            longit = geo[1]
        else:
            div_info = cont[-1].text.replace(" \r", "").strip().split("\n")
            street_address = " ".join(div_info[:2]).strip()
            city, state, zip_code = addy_extractor(
                div_info[-1].strip().replace("  ", ", ")
            )

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
