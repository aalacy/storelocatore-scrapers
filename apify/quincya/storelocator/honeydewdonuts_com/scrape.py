from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://honeydewdonuts.com/wp-json/acf/v3/business_locations?_embed&per_page=300"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    for i in stores:
        store = i["acf"]
        locator_domain = "honeydewdonuts.com"
        street_address = store["address_line_1"]
        city = store["city"]
        state = store["state"]
        zip_code = store["postal_code"]
        country_code = "US"
        phone = store["primary_phone"].strip()
        store_number = store["store_id"]
        location_name = "Honey Dew Donuts #" + store_number
        location_type = ""
        latitude = store["latitude"]
        longitude = store["longitude"]

        hours_of_operation = ""
        hours = store["hours"]
        for row in hours:
            hours_of_operation = (
                hours_of_operation
                + " "
                + row["day"]
                + " "
                + row["start_time"]
                + "-"
                + row["end_time"]
            ).strip()

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url="https://honeydewdonuts.com/locations/",
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
