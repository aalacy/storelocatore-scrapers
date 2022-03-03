from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.lush.cl/nuestras-tiendas/"
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.lush.cl/"

    items = base.find(class_="entry-content").find_all(class_="vc_column-inner")
    for item in items:
        if "direcci" not in item.text.lower():
            continue
        location_name = item.find(class_="titulotienda").text.strip()
        raw_address = list(item.p.stripped_strings)[1]
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        city = addr.city
        if "14 norte 976" in raw_address:
            city = "Viña del Mar"
            raw_address = raw_address + " Viña del Mar"
        state = addr.state
        zip_code = addr.postcode
        country_code = "CL"
        location_type = ""
        store_number = ""
        phone = item.find_all("p")[-1].text.replace("Teléfono", "").strip()
        if "+" not in phone:
            phone = ""
        hours_of_operation = ""
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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
