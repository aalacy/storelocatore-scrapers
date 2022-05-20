import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("lemacaron-us_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://lemacaron-us.com/locations"
    js_link = "https://lemacaron-us.com/oak/themes/lemac/js/nine.min356.js"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    items = base.find_all(class_="location-links")

    js_req = session.get(js_link, headers=headers)
    js = BeautifulSoup(js_req.text, "lxml")
    js = js.text.split("js =")[1].split(";function")[0]
    stores = json.loads(js)

    locator_domain = "lemacaron-us.com"

    for item in items:

        link = "https://lemacaron-us.com" + item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if (
            "COMING SOON" in base.h2.text.upper()
            or "COMING SOON" in base.find(class_="text-fade px-2 mb-2").text.upper()
        ):
            continue

        logger.info(link)

        location_name = base.h2.span.text

        raw_address = base.find(class_="text-fade px-2 mb-2").text.strip().split("\n")
        street_address = raw_address[0].split(". 2200")[0].strip()
        city = raw_address[1].strip().split(",")[0].strip()

        try:
            state = raw_address[1].strip().split(",")[1].strip().split()[0]
        except:
            continue
        zip_code = raw_address[1].strip().split(",")[1].strip().split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = base.find_all(class_="btn btn-sm btn-primary btn-icon")[-3].text
        if "coming" in phone.lower():
            phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        for store in stores:
            if store["alias"] == item.a["href"].split("=")[1]:
                store_number = store["id"]
                latitude = store["latitude"]
                longitude = store["longitude"]
                hours_of_operation = store["fran_hours"].replace("\r\n", " ")
                hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

                if "(" in hours_of_operation:
                    hours_of_operation = hours_of_operation[
                        : hours_of_operation.find("(")
                    ].strip()
                if not hours_of_operation or "click" in hours_of_operation.lower():
                    hours_of_operation = "<MISSING>"
                break

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
