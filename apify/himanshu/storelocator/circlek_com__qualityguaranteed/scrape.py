import csv
import json

import lxml.html

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("circlek.com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.circlek.com"

    found_poi = []
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    location_urls = [
        "https://www.circlek.com/stores_new.php?lat=33.6&lng=-112.12&distance=10000000&services=gas&region=global",
        "https://www.circlek.com/stores_new.php?lat=33.6&lng=-112.12&distance=10000000&services=diesel&region=global",
    ]

    for location_url in location_urls:
        stores = session.get(location_url, headers=headers).json()["stores"]
        logger.info("Processing %s links.." % (len(stores)))
        for key in stores.keys():
            if stores[key]["country"].upper() in ["US", "CA", "CANADA"]:
                if (
                    stores[key]["display_brand"] == "Circle K"
                    and stores[key]["op_status"] != "Planned"
                    and stores[key]["op_status"] != "Future"
                ):
                    page_url = "https://www.circlek.com" + stores[key]["url"]
                    if page_url in found_poi:
                        continue
                    found_poi.append(page_url)
                    try:
                        store_req = session.get(page_url, headers=headers)
                    except:
                        continue
                    store_sel = lxml.html.fromstring(store_req.text)
                    json_list = store_sel.xpath(
                        '//script[@type="application/ld+json"]/text()'
                    )
                    for js in json_list:
                        if "LocalBusiness" in js:
                            store_json = json.loads(js)
                            location_name = stores[key]["display_brand"].replace(
                                "&#039;", "'"
                            )
                            if stores[key]["franchise"] == "1":
                                location_type = "Brand Store"
                            else:
                                location_type = "Dealer/Distributor/Retail Partner"

                            phone = store_json["telephone"]
                            street_address = (
                                store_json["address"]["streetAddress"]
                                .replace("  ", " ")
                                .replace("r&#039;", "'")
                                .replace("&amp;", "&")
                                .strip()
                            )
                            if street_address[-1:] == ",":
                                street_address = street_address[:-1]
                            city = (
                                store_json["address"]["addressLocality"]
                                .replace("&#039;", "'")
                                .strip()
                            )
                            state = ""
                            zipp = store_json["address"]["postalCode"].strip()
                            country_code = stores[key]["country"]
                            latitude = store_json["geo"]["latitude"]
                            longitude = store_json["geo"]["longitude"]
                            store_number = stores[key]["cost_center"]
                            raw_address = store_json["name"]

                            if street_address + city + phone + latitude in found_poi:
                                continue
                            found_poi.append(street_address + city + phone + latitude)

                            try:
                                state = (
                                    raw_address.split(",")[-2]
                                    .replace("PEI", "PE")
                                    .strip()
                                )
                                if len(state) > 3:
                                    state = "<MISSING>"
                            except:
                                state = "<MISSING>"
                            hours = store_sel.xpath(
                                '//div[@class="columns large-12 middle hours-wrapper"]/div[contains(@class,"hours-item")]'
                            )
                            hours_list = []
                            for hour in hours:
                                day = "".join(hour.xpath("span[1]/text()")).strip()
                                time = "".join(hour.xpath("span[2]/text()")).strip()
                                hours_list.append(day + ":" + time)

                            hours_of_operation = "; ".join(hours_list).strip()
                            if stores[key]["op_status"] == "Limitation COVID-19":
                                hours_of_operation = "Coming Soon/Limitation COVID-19"

                            if street_address == "" or street_address is None:
                                street_address = "<MISSING>"

                            if city == "" or city is None:
                                city = "<MISSING>"

                            if state == "" or state is None:
                                state = "<MISSING>"

                            if zipp == "" or zipp is None:
                                zipp = "<MISSING>"

                            if latitude == "" or latitude is None:
                                latitude = "<MISSING>"
                            if longitude == "" or longitude is None:
                                longitude = "<MISSING>"

                            if hours_of_operation == "":
                                try:
                                    hours_of_operation = " ".join(
                                        store_sel.xpath(
                                            '//div[@class="columns large-12 middle hours-wrapper"]/text()'
                                        )
                                    ).strip()
                                except:
                                    hours_of_operation = "<MISSING>"

                            if not hours_of_operation:
                                hours_of_operation = "<MISSING>"

                            if "-" not in phone:
                                phone = "<MISSING>"

                            curr_list = [
                                locator_domain,
                                location_name,
                                street_address,
                                city,
                                state,
                                zipp,
                                country_code,
                                store_number,
                                phone,
                                location_type,
                                latitude,
                                longitude,
                                hours_of_operation,
                                page_url,
                            ]
                            yield curr_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
