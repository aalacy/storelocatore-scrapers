from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://twistedsugar.com/wp-admin/admin-ajax.php?action=store_search&lat=40.53512&lng=-112.01596&max_results=500&search_radius=5000&autoload=1"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://twistedsugar.com"

    for store in stores:
        if "coming soon" in store["description"].lower():
            continue
        location_name = store["store"]
        street_address = (store["address"] + " " + store["address2"]).strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = store["id"]
        phone = store["phone"]
        location_type = ""
        latitude = store["lat"]
        longitude = store["lng"]
        if "." not in latitude:
            latitude = ""
            longitude = ""
        hours_of_operation = BeautifulSoup(store["hours"], "lxml").get_text(" ")
        link = store["url"]
        if not link or "://order.twisted" in link:
            link = "https://twistedsugar.com/store-locator/"

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
