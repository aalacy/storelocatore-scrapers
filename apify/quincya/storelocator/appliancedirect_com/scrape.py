import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.appliancedirect.com/contact"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="location")
    locator_domain = "appliancedirect.com"

    for item in items:

        location_name = item.h4.text.strip()

        raw_address = (
            item.span.text.replace("Rd. Kissi", "Rd, Kissi").strip().split(",")
        )
        while True:
            if "FL " not in raw_address[-1]:
                raw_address.pop(-1)
            else:
                break

        street_address = " ".join(raw_address[:-2]).strip()
        street_address = (re.sub(" +", " ", street_address)).strip()
        city = raw_address[-2].strip()
        state = raw_address[-1].strip()[:3].strip()
        zip_code = raw_address[-1][3:9].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = item.a.text.replace("Phone:", "").strip()
        except:
            phone = "<MISSING>"

        hours_of_operation = (
            item.find_all("span")[-1]
            .text.replace("Store Hours:", "")
            .replace("–", "-")
            .strip()
        )

        try:
            map_link = item.find_all("a")[-1]["href"]
            at_pos = map_link.rfind("@")
            latitude = map_link[at_pos + 1 : map_link.find(",", at_pos)].strip()
            longitude = map_link[
                map_link.find(",", at_pos) + 1 : map_link.find(",", at_pos + 15)
            ].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
