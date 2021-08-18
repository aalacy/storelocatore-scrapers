from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    base_url = "https://www.aireserv.com"
    stores = session.post(
        base_url + "/locations/?CallAjax=GetLocations", headers=headers
    ).json()

    for i in range(len(stores)):
        store_data = stores[i]
        if store_data["Country"] == "USA":
            if store_data["ComingSoon"]:
                continue
            store = []
            store.append("https://www.aireserv.com")
            store.append(store_data["FriendlyName"])
            store.append(store_data["Address1"].replace("Rome,GA,", "").strip())
            store.append(store_data["City"])
            store.append(store_data["State"])
            store.append(store_data["ZipCode"].strip())
            store.append("US")
            store.append(store_data["FranchiseLocationID"])
            store.append(store_data["Phone"])
            store.append("<MISSING>")
            store.append(store_data["Latitude"])
            store.append(store_data["Longitude"])
            store.append(
                store_data["LocationHours"]
                if store_data["LocationHours"]
                else "<MISSING>"
            )
            store.append(base_url + store_data["Path"])

            sgw.write_row(
                SgRecord(
                    locator_domain=store[0],
                    location_name=store[1],
                    street_address=store[2],
                    city=store[3],
                    state=store[4],
                    zip_postal=store[5],
                    country_code=store[6],
                    store_number=store[7],
                    phone=store[8],
                    location_type=store[9],
                    latitude=store[10],
                    longitude=store[11],
                    hours_of_operation=store[12],
                    page_url=store[13],
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
