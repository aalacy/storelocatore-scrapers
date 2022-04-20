from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.lionsupermarket.com/locations"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.lionsupermarket.com"

    items = base.find_all(class_="_2Hij5")

    for item in items:
        try:
            location_name = item.p.text
            if "|" in location_name or "reserved" in location_name:
                continue
        except:
            continue
        raw_address = list(item.stripped_strings)
        raw_address[1] = raw_address[1].replace(", Suit", " Suit")
        street_address = raw_address[1].split(",")[0]
        city = raw_address[1].split(",")[1].strip()
        state = raw_address[1].split(",")[2].split()[0].strip()
        zip_code = raw_address[1].split(",")[2].split()[1].strip()
        hours_of_operation = raw_address[2].split("Hours:")[1].strip()
        phone = raw_address[-1]
        latitude = ""
        longitude = ""
        country_code = "US"
        store_number = "<MISSING>"
        location_type = ""

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
