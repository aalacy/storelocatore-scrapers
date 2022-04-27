from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.tillys.com/on/demandware.store/Sites-tillys-Site/default/Stores-FindStores?showMap=false&isAjax=false&location=30030&radius=5000"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    stores = req.json()["stores"]

    locator_domain = "https://www.tillys.com/"

    for store in stores:
        location_name = store["name"]
        if "coming soon" in location_name.lower():
            continue
        if store["hideFromStoreLocator"]:
            continue
        try:
            street_address = (store["address1"] + " " + store["address2"]).strip()
        except:
            street_address = store["address1"]

        if "3710 Route 9" in street_address:
            street_address = "3710 Route 9 Suite H215"

        city = store["city"]
        state = store["stateCode"]
        zip_code = store["postalCode"]
        country_code = store["countryCode"]
        store_number = store["ID"]
        location_type = " ".join(store["storeType"])
        try:
            phone = store["phone"]
        except:
            phone = ""

        if "closed" in location_name.lower():
            hours_of_operation = "Closed"
        else:
            hours_of_operation = ""
            try:
                raw_hours = store["storeHours"]
                days = list(BeautifulSoup(raw_hours, "lxml").div.stripped_strings)
                hours = list(
                    BeautifulSoup(raw_hours, "lxml").find_all("div")[1].stripped_strings
                )
                if len(days) == len(hours):
                    for i in range(len(hours)):
                        if "hours" not in hours[i].lower():
                            hours_of_operation = (
                                hours_of_operation + " " + days[i] + " " + hours[i]
                            ).strip()
            except:
                pass

        latitude = store["latitude"]
        longitude = store["longitude"]
        link = "https://www.tillys.com/store/?StoreID=" + store_number

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
