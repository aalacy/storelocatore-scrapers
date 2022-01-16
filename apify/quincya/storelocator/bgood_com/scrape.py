from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://bgood.com/locations-new-hours"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "bgood.com"

    items = base.find_all(class_="list-item-content")

    for item in items:
        location_name = item.h2.text.strip()
        raw_data = list(item.p.stripped_strings)
        raw_address = raw_data[0].split(",")
        street_address = "".join(raw_address[:-2]).strip()
        city = raw_address[-2].strip()
        state = raw_address[-1].split()[0].strip()
        zip_code = raw_address[-1].split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = ""
        phone = raw_data[-1].strip()
        if len(phone) > 20:
            phone = ""
        hours_of_operation = (
            item.find_all("p")[1].get_text(" ").replace("Hours:", "").strip()
        )
        latitude = ""
        longitude = ""

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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
