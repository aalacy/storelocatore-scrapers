# -*- coding: utf-8 -*-
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

DOMAIN = "westgateresorts.com"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def pull_content(url):
    log.info("Pull content => " + url)
    soup = BeautifulSoup(session.get(url).content, "lxml")
    return soup


def parse_json(soup):
    info = soup.find("script", type="application/ld+json")
    if not info:
        return []
    data = json.loads(info.string)
    return data


def fetch_data():
    base_url = "https://www.westgateresorts.com/explore-destinations/"
    main_soup = pull_content(base_url)
    k = main_soup.find_all("a", {"class": "button resort"})
    log.info("Found {} urls".format(len(k)))

    for i in k:
        store_url = "https://www.westgateresorts.com/" + i["href"]
        soup = pull_content(store_url)
        data = parse_json(soup)
        if len(data) <= 0:
            log.info("skipped")
        else:
            data = data[0]
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

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
