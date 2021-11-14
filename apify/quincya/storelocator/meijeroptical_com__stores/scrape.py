from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("meijeroptical.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.meijeroptical.com/stores/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=HEADERS)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.meijeroptical.com"

    items = base.find_all(class_="store-info")

    for item in items:
        if "STORE CLOSED" in item.text.upper():
            continue

        location_name = item.h4.text.strip()
        final_link = item.a["href"]
        logger.info(final_link)
        street_address = item.find(class_="street").text.strip()
        city_line = item.find(class_="zip-code").text.strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        phone = item.find(class_="phonenumber").text.strip()
        country_code = "US"
        store_number = item["id"]
        location_type = "<MISSING>"

        req = session.get(final_link, headers=HEADERS)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = " ".join(list(base.find(class_="hours").stripped_strings))

        geo = base.find(class_="makemystore")["data-coord"].split(",")
        latitude = geo[0]
        longitude = geo[1]

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
