import csv

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

    base_link = "https://floydsfinecannabis.com/dispensary-locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(
        class_="nectar-button small regular extra-color-1 regular-button"
    )
    locator_domain = "floydsfinecannabis.com"

    for item in items:

        link = item["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()
        street_address = (
            base.find_all(class_="wpb_wrapper")[1]
            .find_all("p")[-1]
            .text.split("\n")[0]
            .split(",")[0]
            .replace("Portland", "")
            .strip()
        )
        city = base.h5.text.split(",")[0].strip()
        state = base.h5.text.split(",")[1].strip()
        zip_code = (
            base.find_all(class_="wpb_wrapper")[1]
            .find_all("p")[-1]
            .text.split("\n")[0][-5:]
            .strip()
        )
        if not zip_code.strip().isdigit():
            zip_code = "<MISSING>"
        if zip_code == "9721":
            zip_code = "97217"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = base.find(class_="map-marker")["data-lat"]
        longitude = base.find(class_="map-marker")["data-lng"]

        phone = base.find_all(class_="wpb_wrapper")[1].find_all("p")[-1].a.text

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
