from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://cdn.agilitycms.com/scotiabank-peru/agencias/list/agencias-abiertas.json?append=1647937862634"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://www.scotiabank.com.pe/"

    for store in stores:
        location_name = store["Nom"]
        raw_address = store["Dir"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if len(street_address) < 10:
            street_address = raw_address
        city = store["Dep"]
        state = store["Dis"]
        zip_code = ""
        country_code = "Peru"
        store_number = ""
        location_type = store["Est"]
        phone = ""
        hours_of_operation = ""
        week = "L-V: " + store["Hor"]
        try:
            sat = store["Sab"]
            hours_of_operation = week + " S: " + sat
        except:
            hours_of_operation = week

        latitude = ""
        longitude = ""
        link = "https://www.scotiabank.com.pe/Personas/centro-informacion/agencias-disponibles"

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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
