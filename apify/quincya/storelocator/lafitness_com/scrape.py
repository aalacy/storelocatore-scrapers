from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lafitness_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://lafitness.com/Pages/FindClub.aspx"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    states = base.find(id="ctl00_MainContent_FindAClub1_cboSelState").find_all(
        "option"
    )[1:]

    found = []
    base_link = "https://lafitness.com/Pages/GetClubLocations.aspx/GetClubLocationsByStateAndZipCode"
    for i in states:
        search = i.text
        logger.info(search)
        js = {"zipCode": "", "state": search}

        stores = session.post(base_link, headers=headers, json=js).json()["d"]

        locator_domain = "lafitness.com"

        for store in stores:
            location_name = store["Description"]
            raw_address = store["Address"].split("<br />")
            street_address = raw_address[0].strip()
            city_line = raw_address[1].strip().split(",")
            city = store["City"]
            state = store["State"]
            zip_code = " ".join(city_line[1].split()[1:]).strip()

            if len(zip_code) > 5:
                country_code = "CA"
            else:
                country_code = "US"

            store_number = store["ClubID"]
            if store_number in found:
                continue
            found.append(store_number)
            location_type = "Premier Club"
            if "signature" in location_name.lower():
                location_type = "Signature Club"
            elif "presale" in location_name.lower():
                location_type = "PreSale Club"
            elif "plus" in location_name.lower():
                location_type = "Premier Plus Club"
            latitude = store["Latitude"]
            longitude = store["Longitude"]

            link = "https://lafitness.com/Pages/" + store["ClubHomeURL"]

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            phone = base.find(id="ctl00_MainContent_lblClubPhone").text.strip()
            phone = phone.split("Reg")[0]

            try:
                hours_of_operation = (
                    " ".join(list(base.find(id="divClubHourPanel").stripped_strings))
                    .replace("CLUB HOURS", "")
                    .strip()
                )
            except:
                continue

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
