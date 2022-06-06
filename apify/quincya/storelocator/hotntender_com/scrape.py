from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.hotntender.com/wp-admin/admin-ajax.php?action=store_search&lat=39.95258&lng=-75.16522&max_results=5&search_radius=10&autoload=1"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://www.hotntender.com"

    for store in stores:
        location_name = store["store"]
        street_address = store["address"].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = store["country"]
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        if not phone:
            phone = "<MISSING>"
        try:
            hours_of_operation = BeautifulSoup(store["hours"], "lxml").get_text(" ")
        except:
            hours_of_operation = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        link = "https://www.hotntender.com/locations/"

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
