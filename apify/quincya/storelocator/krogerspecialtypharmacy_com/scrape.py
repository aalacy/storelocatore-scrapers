from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.krogerspecialtypharmacy.com/contact"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "krogerspecialtypharmacy.com"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="row column_row").find_all("p")

    for i, item in enumerate(items):
        if item.find(class_="fa fa-phone"):
            continue
        raw_data = list(item.stripped_strings)
        location_name = raw_data[0]
        raw_address = raw_data[1].split(",")
        street_address = " ".join(raw_address[:-2]).replace("  ", " ").strip()
        city = raw_address[-2].strip()
        state = raw_address[-1].strip()[:-6].strip()
        zip_code = raw_address[-1][-6:].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = items[i + 1].find(class_="fa fa-phone").find_next("a").text
        hours_of_operation = raw_data[-1]
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
