import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://219health.org/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="entry-content").find_all(
        "div", {"class": re.compile(r"et_pb_row et_pb_row_[0-9]{2}")}
    )
    locator_domain = "219health.org"

    for item in items:
        if not item.a:
            continue

        location_name = "<MISSING>"

        raw_address = list(item.h6.stripped_strings)
        street_address = raw_address[0].strip()
        city = raw_address[-1].split(",")[0].strip()
        state = raw_address[-1].split(",")[1].split()[0].strip()
        zip_code = raw_address[-1].split(",")[1].split()[1].strip()
        country_code = "US"
        store_number = item["class"][-1].split("_")[-1]
        location_type = "<MISSING>"
        phone = item.h4.text.strip()
        hours_of_operation = " ".join(
            list(item.find_all(class_="et_pb_blurb_description")[-1].stripped_strings)
        )

        map_link = item.iframe["src"]
        lat_pos = map_link.rfind("!3d")
        latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
        lng_pos = map_link.find("!2d")
        longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
