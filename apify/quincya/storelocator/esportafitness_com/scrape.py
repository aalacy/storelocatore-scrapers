from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("esportafitness_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://esportafitness.com/Pages/GetClubLocations.aspx/GetClubLocation"

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    session = SgRequests()

    stores = session.post(base_link, headers=headers).json()["d"]

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    for store in stores:

        locator_domain = "esportafitness.com"

        city = store["City"]
        state = store["State"]
        country_code = "US"
        store_number = store["ClubID"]
        location_type = ""
        latitude = store["Latitude"]
        longitude = store["Longitude"]

        link = "https://esportafitness.com/Pages/" + store["ClubHomeURL"]
        logger.info(link)

        final_req = session.get(link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        location_name = item.h1.text.strip()
        street_address = item.find(id="ctl00_MainContent_lblClubAddress").text
        zip_code = item.find(id="ctl00_MainContent_lblZipCode").text
        phone = item.find(id="ctl00_MainContent_lblClubPhone").text.split("Reg")[0]

        hours_of_operation = (
            item.find(id="divClubHourPanel")
            .get_text(" ")
            .replace("pm", "pm ")
            .replace("CLUB HOURS", "")
            .strip()
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
