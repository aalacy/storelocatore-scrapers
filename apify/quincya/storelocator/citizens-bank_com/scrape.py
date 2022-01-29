import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("citizens-bank_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.citizens-bank.com/about/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(
        "div", {"class": re.compile(r"fl-col-group fl-node.+fl-col-group-nested")}
    )
    locator_domain = "citizens-bank.com"

    hours_of_operation = "<MISSING>"
    hours = base.find_all("strong")
    for hour in hours:
        if "DAY" in hour.text:
            hours_of_operation = (
                hour.previous_element.get_text(" ").replace("  ", " ").strip()
            )
            break

    for item in items:
        if "fl-map" not in str(item):
            continue

        location_name = item.h3.text.strip()
        logger.info(location_name)

        raw_address = list(
            item.find(class_="fl-rich-text").find_all("p")[-2].stripped_strings
        )
        if "Citizens Bank" in raw_address[0]:
            raw_address.pop(0)

        street_address = " ".join(raw_address[:-2]).strip()
        city_line = raw_address[-2].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_address[-1]

        map_link = item.iframe["src"]
        req = session.get(map_link, headers=headers)
        maps = BeautifulSoup(req.text, "lxml")
        geo = (
            re.findall(r"\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]", str(maps))[0]
            .replace("[", "")
            .replace("]", "")
            .split(",")
        )
        latitude = geo[0].strip()
        longitude = geo[1].strip()

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
