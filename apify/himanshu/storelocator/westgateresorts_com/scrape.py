# -*- coding: utf-8 -*-
import csv
import json
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


def parse_json(soup):
    info = soup.find("script", type="application/ld+json").string
    data = json.loads(info)
    return data


def fetch_data():
    base_url = "https://www.westgateresorts.com/explore-destinations/"
    main_soup = pull_content(base_url)
    locations = []
    k = main_soup.find_all("a", {"class": "button resort"})
    log.info("Found {} urls".format(len(k)))

    for i in k:
        store_url = "https://www.westgateresorts.com/" + i["href"]
        soup = pull_content(store_url)
        data = parse_json(soup)[0]
        location_name = data["name"]
        street_address = data["address"]["streetAddress"]
        city = data["address"]["addressLocality"]
        state = data["address"]["addressRegion"]
        zip_code = data["address"]["postalCode"]
        phone = data["telephone"]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "westgateresorts"
        latitude = data["geo"]["latitude"]
        longitude = data["geo"]["longitude"]
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
