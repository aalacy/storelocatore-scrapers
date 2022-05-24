import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("gqtmovies_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.gqtmovies.com/theaterinfo"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.gqtmovies.com"

    items = base.find_all("picture")

    for item in items:
        if str(item.find_next("div")).count("details") == 0:
            continue
        item = item.find_next("div")
        raw_address = list(item.stripped_strings)[:-1]
        location_name = raw_address[0].strip()
        street_address = raw_address[1].strip()
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        link = locator_domain + item.a["href"]

        if "coming-soon" in link:
            continue
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        try:
            phone = base.find("a", {"href": re.compile(r"tel:")}).text
        except:
            phone = "<MISSING>"
        if not phone:
            phone = "<MISSING>"

        map_link = base.find(string="Get directions").find_previous("a")["href"]
        latitude = map_link[map_link.rfind("/") + 1 : map_link.rfind(",")].strip()
        longitude = map_link[map_link.rfind(",") + 1 :].strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
