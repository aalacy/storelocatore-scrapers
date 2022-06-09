from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://texadelphia.com/wp-admin/admin-ajax.php?action=store_search&lat=32.77666&lng=-96.79699&max_results=25&search_radius=100&filter=18&autoload=1"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://texadelphia.com"

    for store in stores:
        location_name = store["store"]
        street_address = (store["address"] + " " + store["address2"]).strip()
        street_address = street_address.replace("4B,", "4B")
        city = store["city"]
        state = store["state"]
        if city == "Dallas":
            state = "Texas"
        zip_code = store["zip"]
        country_code = store["country"]
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        try:
            hours_of_operation = BeautifulSoup(store["hours"], "lxml").get_text(" ")
        except:
            hours_of_operation = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=locator_domain,
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
