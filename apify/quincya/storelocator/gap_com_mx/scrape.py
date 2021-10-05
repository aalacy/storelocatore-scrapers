from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.gap.com.mx/getallstores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    json = {"storeType": "gap"}
    stores = session.post(base_link, headers=headers, json=json).json()["StoreDetails"][
        "stores"
    ]

    locator_domain = "https://www.gap.com.mx"

    for store in stores:

        store_number = store["storeId"]
        location_name = "GAP"
        city = store["city"]
        state = store["state"]
        zip_code = store["postalCode"]
        country_code = "MX"
        location_type = "<MISSING>"
        latitude = store["lpLatitude"]
        longitude = store["lpLongitude"]

        json = {"storeId": store_number}
        store_det = session.post(
            "https://www.gap.com.mx/getstoredetails", headers=headers, json=json
        ).json()["storeDetails"]["StoreDetails"]["1"]

        phone = store_det["phone"]
        street_address = store_det["generalDetails"].split("<")[0]
        country_code = store_det["country"]
        hours_of_operation = store_det["generalDetails"].split(": ")[-1].split("<")[0]
        link = "https://www.gap.com.mx/tienda/browse/storelocator"

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
