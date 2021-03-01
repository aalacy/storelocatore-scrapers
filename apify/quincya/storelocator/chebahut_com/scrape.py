import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgselenium import SgChrome


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

    base_link = "https://chebahut.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    all_links = []

    items = base.find_all("h2", {"class": re.compile(r"title-heading.+")})
    raw_links = base.find_all(class_="fusion-column-inner-bg hover-type-none")
    for raw_link in raw_links:
        all_links.append(raw_link.a["href"])

    locator_domain = "chebahut.com"

    driver = SgChrome(user_agent=user_agent).driver()

    for i, link in enumerate(all_links):
        raw_address = items[i].text.split(",")
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[-1].strip()
        zip_code = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "coming soon" in base.find(class_="post-content").text.lower():
            continue

        driver.get(link)

        base = BeautifulSoup(driver.page_source, "lxml")

        location_name = "CHEBA HUT - " + base.h1.text.strip()
        if location_name == "CHEBA HUT - ":
            location_name = "CHEBA HUT - " + city

        raw_data = list(base.find(class_="content-container").stripped_strings)

        phone = raw_data[1].replace("TBA", "<MISSING>")
        hours_of_operation = " ".join(raw_data[4:])

        if (
            not hours_of_operation
            or "opening" in hours_of_operation.lower()
            or "Monday: Tuesday: Wednesday: Thursday: Friday: Saturday: Sunday:"
            in hours_of_operation
        ):
            continue

        try:
            script = base.find(id="mfLocationJsonLD").contents[0]
            store = json.loads(script)
            city = store["address"]["addressLocality"]
            state = store["address"]["addressRegion"]
            zip_code = store["address"]["postalCode"]
            latitude = store["geo"]["latitude"]
            longitude = store["geo"]["longitude"]
        except:
            script = str(base.find(class_="wpgmza_map"))
            latitude = script.split('map_start_lat":"')[1].split('",')[0]
            longitude = script.split('map_start_lng":"')[1].split('",')[0]

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
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
