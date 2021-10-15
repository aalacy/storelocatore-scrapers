import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("buildabear.ae")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.buildabear.ae/store"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="store_menu_items subitems")
    locator_domain = "https://www.buildabear.ae/"

    for item in items:
        link = locator_domain + item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.h1.text.strip()
        log.info(location_name)
        addr = parse_address_intl(base.find(class_="address-content").p.text)
        street_address = (
            base.find(class_="address-content")
            .text.strip()
            .split("\n")[1]
            .split(", Abu")[0]
            .replace("\xa0", " ")
            .replace("â€‹", "")
            .strip()
        )
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = base.find(class_="address-content").text.strip().split("\n")[-1]
        store_number = link.split("=")[-1]
        location_type = "<MISSING>"
        phone = base.find(class_="address-content").text.strip().split("\n")[2]
        if "+" not in phone:
            phone = ""
        hours_of_operation = ""

        try:
            map_link = base.iframe["src"]
            req = session.get(map_link, headers=headers)
            map_str = BeautifulSoup(req.text, "lxml")
            geo = re.findall(r"[0-9]{2}\.[0-9]+,[0-9]{2,3}\.[0-9]+", str(map_str))[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = "<INACCESSBILE>"
            longitude = "<INACCESSBILE>"

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
                raw_address=item.a.text,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
