from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://pizzapro.com/src/scripts/load-locations-csv.php"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()[1:]

    locator_domain = "pizzapro.com"

    for store in store_data:
        location_name = ""
        try:
            street_address = store[2]
        except:
            continue
        city = store[0].split("(")[0]
        try:
            city = city.split("/")[1].strip()
        except:
            pass
        state = store[1]
        if not state:
            continue
        zip_code = store[3]
        country_code = "US"
        location_type = ""
        phone = store[4].split("/")[0]
        hours_of_operation = ""
        link = "https://pizzapro.com/store-locator"
        store_number = ""
        latitude = ""
        longitude = ""

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


with SgWriter(
    SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.CITY, SgRecord.Headers.STATE, SgRecord.Headers.PHONE}
        )
    )
) as writer:
    fetch_data(writer)
