from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://mitsubishi-motors.co.uk/wp/wp-admin/admin-ajax.php?action=store_search&lat=52.35552&lng=-1.17432&max_results=&search_radius=&filter=19&autoload=1"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "mitsubishi-motors.co.uk"

    for store in stores:
        location_name = store["store"].replace("&#8217;", "'").replace("#038;", "")
        street_address = (store["address"] + " " + store["address2"]).strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = "UK"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        latitude = store["lat"]
        longitude = store["lng"]
        hours_of_operation = " ".join(
            list(BeautifulSoup(store["hours"], "lxml").stripped_strings)
        )
        link = "https://mitsubishi-motors.co.uk/dealer-locator/"

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
