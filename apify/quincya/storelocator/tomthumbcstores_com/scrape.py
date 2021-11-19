from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.tomthumbcstores.com/StoreData/GetStoreDataByLocation?location=27.6648274%2C-81.5157535&currentPageId=3036"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "tomthumbcstores.com"

    for store in stores:
        location_name = "Tom Thumb - " + store["City"]
        street_address = store["Address"]
        city = store["City"]
        state = store["State"]
        zip_code = store["Zip"]
        country_code = "US"
        store_number = store["StoreId"]
        location_type = "<MISSING>"
        phone = store["Phone"]
        hours_of_operation = "<MISSING>"
        latitude = store["Latitude"]
        longitude = store["Longitude"]
        link = "https://www.tomthumbcstores.com/store-locator/"

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

with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
