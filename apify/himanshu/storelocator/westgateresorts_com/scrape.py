# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import sglog

DOMAIN = "westgateresorts.com"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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


def pull_content(url):
    log.info("Pull content => " + url)
    soup = BeautifulSoup(session.get(url).content, "lxml")
    return soup


def fetch_data():
    base_url = "https://www.westgateresorts.com/explore-destinations/"
    main_soup = pull_content(base_url)
    locations = []
    k = main_soup.find_all("a", {"class": "button resort"})
    log.info("Found {} urls".format(len(k)))

    for i in k:
        store_url = "https://www.westgateresorts.com/" + i["href"]
        soup = pull_content(store_url)
        info = soup.find("div", {"id": "footer-resort-info"})
        if not info:
            if "westgate-new-york-grand-central" in store_url:
                info = soup.find(
                    "div", {"class": "footer__connect__address"}
                ).stripped_strings
                data = list(info)
                data.remove("Address:")
                resort_phone = soup.find(
                    "div", {"class": "footer__connect__resort-phone"}
                ).get_text(strip=True, separator="")
                data.append(resort_phone)
            else:
                continue
        else:
            data = list(info.stripped_strings)
        location_name = data[0]
        street_address = data[1]
        city_zip = data[2]
        city = city_zip.split(",")[0]
        state = city_zip.split(",")[1].split()[0]
        zip_code = city_zip.split(",")[1].split()[1]
        phone = data[3].split("Resort Phone:")[1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "westgateresorts"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                DOMAIN,
                store_url,
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
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
