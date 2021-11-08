from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("shopnsavefood_com")


def addy_ext(addy):
    addy = addy.split(",")
    city = addy[0]
    state_zip = addy[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.shopnsavefood.com/"
    ext = "StoreLocator/Search/?ZipCode=10001&miles=10000"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    link_list = base.find(id="StoreLocator").find_all("a")

    for i in link_list:
        link = (
            "https://shopnsavefood.com/StoreLocator/Store/?" + i["href"].split("?")[1]
        )
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h3.text
        addy = list(base.find(class_="Address").stripped_strings)
        street_address = addy[1]
        city, state, zip_code = addy_ext(addy[2])
        phone_number = " ".join(base.find(class_="PhoneNumber").a.stripped_strings)
        hours = " ".join(base.find(id="hours_info-BS").dd.stripped_strings)
        country_code = "US"
        geo = str(base).split("initializeMap(")[1].split(")")[0].split(",")
        lat = geo[0].replace('"', "")
        longit = geo[1].replace('"', "")
        location_type = "<MISSING>"
        store_number = link.split("=")[1].split("&")[0]

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
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
