from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "winndixie.com"

    store_link = "https://www.winndixie.com/V2/storelocator/getStores?search=jacksonville,%20fl&strDefaultMiles=1000&filter="

    stores = session.get(store_link, headers=headers).json()

    for store in stores:
        location_name = store["StoreName"]
        street_address = store["Address"]["AddressLine2"].strip()
        if not location_name:
            location_name = "Winn-Dixie At " + street_address
        city = store["Address"]["City"]
        state = store["Address"]["State"]
        zip_code = store["Address"]["Zipcode"]
        country_code = "US"
        store_number = store["StoreCode"]
        location_type = store["StoreBannerTypDesc"]
        phone = store["Phone"]
        hours_of_operation = store["WorkingHours"].strip()
        latitude = store["Address"]["Latitude"]
        longitude = store["Address"]["Longitude"]
        if str(latitude) == "0":
            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"
        link = "https://www.winndixie.com/storedetails?search=" + str(
            store["StoreCode"]
        )

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

    fuel_link = "https://www.winndixie.com/V2/storelocator/getFuelStores"
    fuel_stores = []
    try:
        js = {"search": "jacksonville, fl", "strDefaultMiles": "200"}
        fuel_stores = session.post(fuel_link, headers=headers, json=js).json()[
            "locations"
        ]
    except:
        pass
    for store in fuel_stores:
        location_name = store["name"]
        street_address = store["address"]["street1"].strip()
        city = store["address"]["city"]
        state = store["address"]["stateCode"]
        zip_code = store["address"]["zipCode"]
        country_code = "US"
        store_number = str(int(store["id"]))
        location_type = "Fuel"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]

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
