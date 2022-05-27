from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lafitness_com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json; charset=utf-8",
        "Host": "lafitness.com",
        "Origin": "https://lafitness.com",
        "Referer": "https://lafitness.com/Pages/FindClub.aspx",
        "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "document",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    base_link = "https://lafitness.com/Pages/GetClubLocations.aspx/GetClubLocation"

    stores = session.post(base_link, headers=headers).json()["d"]

    locator_domain = "lafitness.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    logger.info("Found " + str(len(stores)) + " stores ..")
    for store in stores:
        location_name = store["Description"]
        if "esporta" in location_name.lower():
            continue
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
            hours_of_operation = "<MISSING>"

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
