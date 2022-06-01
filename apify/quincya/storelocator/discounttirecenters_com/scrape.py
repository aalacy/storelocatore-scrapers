import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.discounttirecenters.com/stores/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.discounttirecenters.com/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = str(base).split("m35_retailers = ")[1].split("];")[0] + "]"

    stores = json.loads(js)

    for store in stores:
        location_name = store["Name"]
        street_address = (
            store["Location"]["Address1"]
            + " "
            + store["Location"]["Address2"]
            + " "
            + store["Location"]["Address3"]
        ).strip()
        city = store["Location"]["City"]
        state = store["Location"]["State"]
        zip_code = store["Location"]["PostCode"]
        phone = store["Phone"]
        latitude = store["Location"]["Latitude"]
        longitude = store["Location"]["Longitude"]
        store_number = store["ID"]
        country_code = "US"
        location_type = "<MISSING>"
        link = (
            "https://www.discounttirecenters.com/stores/view/" + store["CustomField7"]
        )

        hours_of_operation = (
            "Monday "
            + store["OpeningTimes"]["MondaySchedule"]
            + " Tuesday "
            + store["OpeningTimes"]["TuesdaySchedule"]
            + " Wednesday "
            + store["OpeningTimes"]["WednesdaySchedule"]
            + " Thursday "
            + store["OpeningTimes"]["ThursdaySchedule"]
            + " Friday "
            + store["OpeningTimes"]["FridaySchedule"]
            + " Saturday "
            + store["OpeningTimes"]["SaturdaySchedule"]
            + " Sunday "
            + store["OpeningTimes"]["SundaySchedule"]
        )

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
