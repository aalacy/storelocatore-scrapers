import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("elpuente.com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://delpuente.com.gt/restaurantes/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://delpuente.com.gt"

    response = session.get(base_link, headers=headers)
    base = BeautifulSoup(response.text, "lxml")

    items = base.find(class_="sub-menu").find_all("a")
    log.info("Locations found: " + str(len(items)))

    for item in items:
        link = item["href"]
        log.info(link)

        response = session.get(link, headers=headers)
        base = BeautifulSoup(response.text, "lxml")

        location_name = base.find(class_="et_pb_text_inner").text.strip()

        raw_address = base.p.text.strip()
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        if len(street_address) < 15:
            street_address = raw_address.split("Centro")[0].strip()
        country_code = "Guatemala"
        store_number = ""
        location_type = ""
        phone = base.find(class_="entry-content").a.text
        hours_of_operation = ""
        map_link = base.find(class_="entry-content").find_all("a")[1]["href"]
        try:
            geo = re.findall(r"[0-9]{1,2}\.[0-9]+%2C-[0-9]{2,3}\.[0-9]+", map_link)[
                0
            ].split("%2C")
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
