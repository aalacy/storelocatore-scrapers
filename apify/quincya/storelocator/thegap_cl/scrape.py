from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgpostal.sgpostal import parse_address_intl


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.thegap.cl/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.thegap.cl/horario-nuestras-tiendas"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="pagebuilder-column-group")

    for item in items:
        location_name = item.find(class_="pagebuilder-column").text
        try:
            raw_address = item.find_all(class_="pagebuilder-column")[1].text.replace(
                "\n", " "
            )
        except:
            continue
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "Chile"
        store_number = ""
        location_type = ""
        phone = ""
        latitude = ""
        longitude = ""
        hours_of_operation = (
            item.find_all(class_="pagebuilder-column")[2]
            .text.replace("\n", " ")
            .strip()
        )

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
