import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("marciano.com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    final_links = []

    base_links = [
        "https://stores.marciano.com/ca/en/browse/",
        "https://stores.marciano.com/us/en/browse/",
    ]

    for base_link in base_links:
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        main_items = base.find(class_="browse-mode-list").find_all(class_="ga-link")
        for main_item in main_items:
            main_link = main_item["href"]

            logger.info("Processing: " + main_link)
            req = session.get(main_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            next_items = base.find(class_="map-list").find_all(class_="ga-link")
            for next_item in next_items:
                next_link = next_item["href"]
                next_req = session.get(next_link, headers=headers)
                next_base = BeautifulSoup(next_req.text, "lxml")

                other_links = next_base.find(class_="map-list").find_all("li")
                for other_link in other_links:
                    link = other_link.a["href"]
                    final_links.append(link)

    logger.info("Processing %s links ..." % (len(final_links)))
    for final_link in final_links:
        logger.info(final_link)
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "marciano.com"

        script = item.find("script", attrs={"type": "application/ld+json"}).contents[0]
        store = json.loads(script)[0]
        try:
            location_name = item.h2.text.strip()
        except:
            location_name = store["name"]
        street_address = store["address"]["streetAddress"].strip()
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = "US"
        if "/ca/" in final_link:
            country_code = "CA"
        try:
            location_type = ", ".join(
                list(item.find(class_="features-section").stripped_strings)[1:]
            )
        except:
            location_type = "<MISSING>"
        phone = store["address"]["telephone"]
        if not phone:
            phone = "<MISSING>"
        if not location_name:
            location_name = "<MISSING>"
        store_number = final_link.split("-")[-1].split(".")[0]
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        try:
            hours_of_operation = " ".join(
                list(item.find(class_="hours").stripped_strings)
            )
        except:
            hours_of_operation = store["openingHours"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=final_link,
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
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
