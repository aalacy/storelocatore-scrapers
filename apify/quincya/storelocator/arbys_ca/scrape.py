import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("arbys_ca")


def fetch_data(sgw: SgWriter):

    base_link = "https://locations.arbys.ca/browse/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []

    main_items = base.find(class_="browse mb-50").find_all(class_="ga-link")
    for main_item in main_items:
        main_link = main_item["href"]

        logger.info("Processing: " + main_link)
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        next_items = base.find(class_="inner-container").find_all(class_="ga-link")
        for next_item in next_items:
            link = next_item["href"]
            next_req = session.get(link, headers=headers)
            next_base = BeautifulSoup(next_req.text, "lxml")

            other_links = next_base.find_all(class_="location-name ga-link")
            for other_link in other_links:
                new_link = other_link["href"]
                if new_link not in final_links:
                    final_links.append(new_link)

    logger.info("Processing %s links ..." % (len(final_links)))
    for final_link in final_links:
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "arbys.ca"

        script = item.find("script", attrs={"type": "application/ld+json"}).contents[0]
        try:
            store = json.loads(script)[0]
        except:
            store = json.loads(script.split('"additiona')[0].strip()[:-1] + "}]")[0]
        try:
            location_name = item.find(class_="location-name").text.strip()
        except:
            location_name = store["name"]
        street_address = store["address"]["streetAddress"].strip()
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        if not zip_code:
            zip_code = "<MISSING>"
        country_code = "CA"
        try:
            location_type = ", ".join(
                list(item.find(class_="location-features-wrap mb-0").stripped_strings)
            )
        except:
            location_type = "<MISSING>"
        phone = store["address"]["telephone"]
        if not phone:
            phone = "<MISSING>"
        try:
            store_number = (
                item.find(class_="address")
                .find_all("span")[-1]
                .text.replace("Store ID:", "")
                .strip()
            )
        except:
            store_number = ""
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        try:
            hours_of_operation = " ".join(
                list(item.find(class_="hours").stripped_strings)
            )
        except:
            hours_of_operation = "<MISSING>"

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
