from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.pacsun.com/on/demandware.store/Sites-pacsun-Site/default/Stores-FindStores?showMap=false&radius=5000&findInStore=false&postalCode=43240"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    stores = session.get(base_link, headers=headers).json()["stores"]

    locator_domain = "pacsun.com"

    for store in stores:
        location_type = "<MISSING>"
        location_name = store["name"]
        if "CLOSED" in location_name.upper():
            location_type = "Closed"
        try:
            street_address = (store["address1"] + " " + store["address2"]).strip()
        except:
            street_address = store["address1"]
        city = store["city"]
        state = store["stateCode"]
        zip_code = store["postalCode"]
        country_code = store["countryCode"]
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        store_number = store["ID"]
        hours_of_operation = BeautifulSoup(store["storeHours"], "lxml").get_text(" ")

        link = "https://www.pacsun.com/store?id=" + str(store_number)

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
