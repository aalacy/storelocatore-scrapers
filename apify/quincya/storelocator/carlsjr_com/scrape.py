from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("carlsjr.com")


def fetch_data(sgw: SgWriter):
    base_link = "https://locations.carlsjr.com/index.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.carlsjr.com/"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    main_items = base.find_all(class_="Directory-listLink")

    final_links = []
    for main_item in main_items:
        link = "https://locations.carlsjr.com/" + main_item["href"]
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        next_items = base.find_all(class_="Directory-listLink")
        for next_item in next_items:
            next_link = "https://locations.carlsjr.com/" + next_item["href"].replace(
                "../", ""
            )
            if next_item["href"].count("/") > 1:
                final_links.append(next_link)
            else:
                req = session.get(next_link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                last_items = base.find_all(class_="Teaser-ctaLink")
                for last_item in last_items:
                    last_link = "https://locations.carlsjr.com/" + last_item[
                        "href"
                    ].replace("../", "")
                    final_links.append(last_link)

    logger.info("Processing " + str(len(final_links)) + " links ...")
    for final_link in final_links:
        final_link = final_link.replace("--", "-")
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.h1.text.strip()

        street_address = base.find(itemprop="streetAddress")["content"]
        state = base.find(itemprop="addressRegion").text.strip()
        zip_code = base.find(itemprop="postalCode").text.strip()
        city = base.find(class_="Address-field Address-city").text.strip()
        country_code = "US"

        try:
            phone = base.find(itemprop="telephone").text.strip()
            if not phone:
                phone = ""
        except:
            phone = ""
        try:
            store_number = base.main["itemid"].split("#")[1]
        except:
            store_number = ""

        try:
            location_type = ", ".join(
                list(base.find(class_="Core-featuresList").stripped_strings)
            )
        except:
            location_type = ""

        try:
            hours_of_operation = (
                " ".join(list(base.find(class_="c-hours-details").stripped_strings))
                .replace("Day of the Week Hours", "")
                .strip()
            )
        except:
            hours_of_operation = ""

        latitude = base.find(itemprop="latitude")["content"]
        longitude = base.find(itemprop="longitude")["content"]

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
