import re

from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.carlsjr.jp/location.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.carlsjr.jp"

    items = base.find(class_="shop-list").find_all("li")

    for item in items:
        if "food truck" in item.text.lower():
            continue
        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.tr.td.text
        raw_address = base.find_all("td")[3].text
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        if not street_address or len(street_address) < 8:
            street_address = raw_address
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "Japan"
        store_number = ""
        location_type = ""
        phone = base.find_all("td")[4].text
        hours_of_operation = (
            base.find_all("td")[1]
            .text.replace("）", ")")
            .replace("（", " (")
            .replace("〜", "-")
            .split(")")[0]
            + ")"
        )
        try:
            geo = re.findall(r"[0-9]{2}\.[0-9]+, [0-9]{2,3}\.[0-9]+", str(base))[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1].strip()
        except:
            latitude = ""
            longitude = ""

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
