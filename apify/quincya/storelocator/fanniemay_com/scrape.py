import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("fanniemay.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://locations.fanniemay.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []

    main_items = base.find(class_="no-results").find_all(class_="ga-link")
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

            other_links = next_base.find(class_="map-list").find_all(
                class_="map-list-item-header"
            )
            for other_link in other_links:
                link = other_link.a["href"]
                final_links.append(link)

    logger.info("Processing %s links ..." % (len(final_links)))
    for final_link in final_links:
        logger.info(final_link)
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "fanniemay.com"

        script = item.find("script", attrs={"type": "application/ld+json"}).contents[0]
        try:
            store = json.loads(script)[0]
        except:
            store = json.loads(script.split('"additiona')[0].strip()[:-1] + "}]")[0]
        try:
            location_name = item.find(class_="h2").text.strip()
        except:
            location_name = store["name"]
        street_address = store["address"]["streetAddress"].strip()
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        if not zip_code:
            zip_code = "<MISSING>"
        country_code = "US"
        try:
            location_type = ", ".join(
                list(item.find(class_="store-features").ul.stripped_strings)
            )
        except:
            location_type = "<MISSING>"
        phone = store["address"]["telephone"]
        if not phone:
            phone = "<MISSING>"
        if not location_name:
            location_name = "<MISSING>"
        store_number = item.find(class_="map-list").div["data-fid"]
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
