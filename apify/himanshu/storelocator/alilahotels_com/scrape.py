import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import lxml.html

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.alilahotels.com/ventana",
        "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    base_url = "https://www.alilahotels.com"
    r = session.get("https://www.alilahotels.com/destinations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for country in soup.find_all(
        "div", {"class": "footer__column grid__item footer__column--destinations"}
    ):
        if "United States" in list(country.stripped_strings):
            for location in country.find(
                "ul", {"class": "js-list-content footer__list"}
            ).find_all("li", {"class": "footer__list-item"}):
                page_url = location.find("a")["href"]
                location_request = session.get(page_url, headers=headers)
                location_sel = lxml.html.fromstring(location_request.text)
                location_details = None
                try:
                    location_details = json.loads(
                        "".join(
                            location_sel.xpath(
                                '//script[@type="application/ld+json"]/text()'
                            )
                        ).strip()
                    )
                except:
                    location_details = json.loads(
                        "".join(
                            location_sel.xpath(
                                '//script[@type="application/ld+json"]/text()'
                            )
                        )
                        .strip()
                        .rsplit(",", 1)[0]
                        .strip()
                        + "}"
                    )

                latitude = location_details["geo"]["latitude"]
                longitude = location_details["geo"]["longitude"]
                if latitude == "":
                    latitude = "<MISSING>"
                if longitude == "":
                    longitude = "<MISSING>"

                street_address = location_details["address"]["streetAddress"].split(
                    ","
                )[0]
                if street_address == "":
                    street_address = "<MISSING>"

                store = []
                store.append(base_url)
                store.append(location_details["name"])
                store.append(street_address)
                store.append(
                    location_details["address"]["addressLocality"]
                    if location_details["address"]["addressLocality"] != ""
                    else "<MISSING>"
                )
                store.append(
                    location_details["address"]["addressRegion"]
                    .replace(",", "")
                    .strip()
                    if location_details["address"]["addressRegion"] != ""
                    else "<MISSING>"
                )
                store.append(
                    location_details["address"]["postalCode"]
                    if location_details["address"]["postalCode"] != ""
                    else "<MISSING>"
                )
                store.append("US")
                store.append("<MISSING>")
                store.append(location_details["telephone"])
                store.append("alila")
                store.append(latitude)
                store.append(longitude)
                store.append("<MISSING>")
                store.append(page_url)
                return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
