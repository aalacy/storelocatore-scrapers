import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    locator_domain = "<MISSING>"
    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zip_code = "<MISSING>"
    country_code = "<MISSING>"
    location_no = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    regions = []
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }
    locator_domain = "https://renaissance-hotels.marriott.com"
    base_url = "https://renaissance-hotels.marriott.com/locations-list-view"
    base_res = session.get(base_url, headers=headers)
    base_soup = BeautifulSoup(base_res.text, "html5lib")
    regions = base_soup.find_all(class_="locations-list__regions")
    for region in regions:
        if region.find(class_="locations-list__region heading-large").text in [
            "Canada",
            "United States",
        ]:
            for hotel in region.find_all(class_="locations-list__hotel"):
                link = hotel.find("a")
                city = link.text.split(",")[0]
                location_name = link.text.split(",")[1].strip()
                url = link.get("href")
                page_url = locator_domain + "/" + url
                page_res = session.get(page_url, headers=headers)
                if page_res.status_code == 200:
                    page_soup = BeautifulSoup(page_res.text, "html5lib")
                    position = page_soup.find("meta", {"name": "geo.position"})
                    if position != None:
                        co_ord = position.get("content")
                        latitude = co_ord.split(";")[0]
                        longitude = co_ord.split(";")[1]
                        page_data = page_soup.find_all(
                            class_="l-l-display-inline-block is-hidden-s t-line-height-m t-color-brand"
                        )
                        street_address = page_data[0].text
                        state = page_data[2].text
                        zip_code = page_data[3].text
                        country_code = page_data[4].text
                        phone = page_soup.find(
                            class_="phone-number t-color-brand t-font-s t-line-height-m l-l-display-inline-block is-hidden-s l-phone-number t-force-ltr"
                        ).text
                    else:
                        script = page_soup.find(
                            "script", {"type": "application/ld+json"}
                        ).text
                        data = (
                            script.replace("\xa0\n", "")
                            .replace(".\n", "")
                            .replace('\n"', '"')
                        )
                        json_data = json.loads(data)
                        latitude = json_data["geo"]["latitude"]
                        longitude = json_data["geo"]["longitude"]
                        street_address = json_data["address"]["streetAddress"]
                        state = json_data["address"]["addressLocality"]
                        zip_code = json_data["address"]["postalCode"]
                        country_code = json_data["address"]["addressCountry"]
                        phone = json_data["contactPoint"][0]["telephone"]

                location = []
                location.append(locator_domain if locator_domain else "<MISSING>")
                location.append(location_name if location_name else "<MISSING>")
                location.append(street_address if street_address else "<MISSING>")
                location.append(city if city else "<MISSING>")
                location.append(state if state else "<MISSING>")
                location.append(zip_code if zip_code else "<MISSING>")
                location.append(country_code if country_code else "<MISSING>")
                location.append(location_no if location_no else "<MISSING>")
                location.append(phone if phone else "<MISSING>")
                location.append(location_type if location_type else "<MISSING>")
                location.append(latitude if latitude else "<MISSING>")
                location.append(longitude if longitude else "<MISSING>")
                location.append(
                    hours_of_operation if hours_of_operation else "<MISSING>"
                )
                location.append(page_url if page_url else "<MISSING>")
                yield location


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
