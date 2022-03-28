from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://cpk.com.mx/wp-admin/admin-ajax.php?action=store_search&lat=0&lng=0&max_results=25&search_radius=50&autoload=1"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://cpk.com.mx"

    for store in stores:
        location_name = store["store"]
        addr = parse_address_intl(store["address"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = (
                addr.street_address_1 + " " + addr.street_address_2
            ).strip()
        city = store["address2"]
        state = addr.state
        zip_code = addr.postcode
        country_code = "MX"
        store_number = store["id"]
        phone = store["phone"]
        location_type = ""
        latitude = store["lat"]
        longitude = store["lng"]
        hours_of_operation = BeautifulSoup(store["hours"], "lxml").get_text(" ")
        link = "https://cpk.com.mx/sucursales/"

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
                raw_address=store["address"],
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
