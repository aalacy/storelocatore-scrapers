import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.tanztanning.co.uk/salons/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="fusion-li-item-content")
    locator_domain = "https://www.tanztanning.co.uk"

    for item in items:
        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        raw_data = (
            base.find(class_="fusion-text fusion-text-2")
            .text.strip()
            .replace(",\n", ",")
            .replace("\n", ",")
            .split(",")
        )
        street_address = ", ".join(raw_data[:-3]).replace("  ", " ")
        city = raw_data[-3].strip()
        state = ""
        zip_code = raw_data[-2].strip()
        country_code = "UK"
        location_type = ""
        store_number = base.section.div["id"].split("-")[-1]
        phone = raw_data[-1].replace("Tel.", "").strip()
        hours_of_operation = "<INACCESSIBLE>"
        try:
            latitude = (
                re.findall(r'latitude":"[0-9]{2}\.[0-9]+', str(base))[0]
                .split(':"')[1]
                .strip()
            )
            longitude = (
                re.findall(r'longitude":"-[0-9]{1,2}\.[0-9]+', str(base))[0]
                .split(':"')[1]
                .strip()
            )
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
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
