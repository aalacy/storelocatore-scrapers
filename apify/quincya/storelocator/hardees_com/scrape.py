from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("hardees.com")


def fetch_data(sgw: SgWriter):
    base_link = "https://hardees.com/sitemap.xml"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "hardees.com"

    final_links = []
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    items = base.find_all("loc")
    for item in items:
        if (
            "https://locations.hardees.com/" in item.text
            and "/intl/" not in item.text
            and "/pb/" not in item.text
        ):
            link = (
                item.text.replace(",", "")
                .replace("-&", "")
                .replace("-n-w", "-nw")
                .replace("-nwashington", "-n-washington")
                .replace("--", "-")
                .split("-suite")[0]
                .split("-#")[0]
            )
            if link == "https://locations.hardees.com/ar/fort-smith/1820-phoenix-av":
                link = "https://locations.hardees.com/ar/fort-smith/1820-phoenix-ave"
            if link == "https://locations.hardees.com/mo/leadington/100-plaza-sq":
                link = "https://locations.hardees.com/mo/leadington/100-plaza-square"
            if "/6164-county" in link:
                link = link.replace("6164-county", "travel-center-6164-county")
            if "/6410-county" in link:
                link = link.replace("6410-county", "travel-center-6410-county")
            final_links.append(link)

    logger.info("Processing " + str(len(final_links)) + " links ..")
    for final_link in final_links:
        final_link = final_link.replace("--", "-")
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.h1.text.strip()

        street_address = base.find(itemprop="streetAddress")["content"]
        state = base.find(itemprop="addressRegion").text.strip()
        zip_code = base.find(itemprop="postalCode").text.strip()

        try:
            city = base.find(class_="c-address-city").text.strip()
        except:
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
