from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.bailapizza.fr/wp-admin/admin-ajax.php?action=store_search&lat=0&lng=0&max_results=25&search_radius=5000&autoload=1"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://www.bailapizza.fr"

    for store in stores:
        location_name = store["store"].replace("&#8211;", "-")
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = store["country"]
        store_number = store["id"]
        phone = store["phone"]
        location_type = ""
        latitude = store["lat"]
        longitude = store["lng"]
        hours_of_operation = BeautifulSoup(store["hours"], "lxml").get_text(" ")
        link = "https://www.bailapizza.fr/trouver-un-restaurant-baila-pizza-antentico/"

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
