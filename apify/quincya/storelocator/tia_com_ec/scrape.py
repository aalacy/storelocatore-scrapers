from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.corporativo.tia.com.ec/locals/SearchLocalsMap?state=&city=&localname="

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://www.corporativo.tia.com.ec"

    for store in stores:
        location_name = store["Name"]
        raw_address = store["Address"]
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        if len(street_address) < 15:
            street_address = raw_address
        city = store["City"]
        state = store["State"]
        zip_code = addr.postcode
        country_code = "Ecuador"
        store_number = store["LocalCode"]
        location_type = ""
        phone = store["Phone"]
        hours_of_operation = ""
        latitude = store["Latitude"]
        longitude = store["Longitude"].replace("-7843", "-78.43")

        link = "https://www.corporativo.tia.com.ec/atencion-al-cliente/localizador-de-tiendas"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
