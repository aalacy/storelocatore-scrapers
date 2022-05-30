import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cote_co_uk")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.cote.co.uk/wp-content/uploads/locations.js"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=HEADERS)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "cote.co.uk"

    stores = json.loads(base.text.replace("var locationList =", "").strip())

    for store in stores:
        link = store["link"]

        if "/test/" in link:
            continue
        logger.info(link)

        location_name = store["post_title"]
        street_address = (
            (store["address_1"] + " " + store["address_2"]).replace("`", "'").strip()
        )
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city = store["town_city"]
        state = "<MISSING>"
        zip_code = store["postcode"]
        country_code = "GB"
        store_number = store["ID"]
        phone = store["phone_number"]
        try:
            latitude = store["location"]["lat"]
            longitude = store["location"]["lng"]
        except:
            latitude = ""
            longitude = ""

        req = session.get(link, headers=HEADERS)
        base = BeautifulSoup(req.text, "lxml")

        location_type = (
            base.find_all(class_="w-6/12 px-1 font-serif text-18 leading-16")[-1]
            .text.replace("Facilities", "")
            .strip()
            .replace("\n\n", "")
            .replace("\n", ",")
            .replace("•", "")
            .replace(" , ", "")
            .strip()
        )
        location_type = (re.sub(" +", " ", location_type)).strip()
        hours_of_operation = (
            base.find_all(class_="w-6/12 px-1 font-serif text-18 leading-16")[-2]
            .text.replace("Opening Times", "")
            .strip()
            .replace("\n\n", "")
            .replace("\n", " ")
            .strip()
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
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
