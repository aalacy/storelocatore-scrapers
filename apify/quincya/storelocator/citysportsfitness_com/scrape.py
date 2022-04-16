import json
from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("citysportsfitness_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.citysportsfitness.com/Pages/GetClubLocations.aspx/GetClubLocationsByStateAndZipCode"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()

    js = {"zipCode": "", "state": "CA"}
    response = session.post(base_link, headers=HEADERS, json=js)
    base = BeautifulSoup(response.text, "lxml")

    stores = json.loads(base.text.strip())["d"]

    locator_domain = "citysportsfitness.com"

    for store in stores:
        location_name = store["Description"]
        raw_address = store["Address"].split("<br />")
        street_address = raw_address[0].strip()
        city_line = raw_address[1].strip().split(",")
        city = store["City"]
        state = store["State"]
        zip_code = city_line[1].split()[1].strip()
        country_code = "US"
        store_number = store["ClubID"]
        location_type = "Premier Club"
        if "signature" in location_name.lower():
            location_type = "Signature Club"
        elif "presale" in location_name.lower():
            location_type = "PreSale Club"
        elif "plus" in location_name.lower():
            location_type = "Premier Plus Club"
        latitude = store["Latitude"]
        longitude = store["Longitude"]

        link = "https://www.citysportsfitness.com/pages/" + store["ClubHomeURL"]
        logger.info(link)

        req = session.get(link, headers=HEADERS)
        base = BeautifulSoup(req.text, "lxml")

        phone = base.find(id="ctl00_MainContent_lblClubPhone").text.strip()

        try:
            hours_of_operation = (
                " ".join(list(base.find(id="divClubHourPanel").stripped_strings))
                .replace("CLUB HOURS", "")
                .strip()
            )
        except:
            hours_of_operation = ""

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
