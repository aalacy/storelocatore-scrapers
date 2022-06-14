from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.superthrifty.com/wp-admin/admin-ajax.php?action=store_search&lat=49.3530784&lng=-97.3899384&max_results=50&search_radius=2000"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests(verify_ssl=False)
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://www.superthrifty.com"

    for store in stores:
        location_name = store["store"].replace("&#8217;", "'")
        street_address = (store["address"] + " " + store["address2"]).strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        if "Otineka" in street_address:
            zip_code = "R9A 1P8"
        country_code = store["country"]
        store_number = store["id"]
        phone = store["phone"]
        location_type = ""
        latitude = store["lat"]
        longitude = store["lng"]
        hours_of_operation = BeautifulSoup(store["hours"], "lxml").get_text(" ")
        link = locator_domain + store["url"]
        if not store["url"]:
            link = "https://www.superthrifty.com/locations/"

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
