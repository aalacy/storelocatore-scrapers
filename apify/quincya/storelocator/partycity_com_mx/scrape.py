from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.partycity.com.mx"
    base_link = "https://www.partycity.com.mx/_v/private/graphql/v1?workspace=master&maxAge=long&appsEtag=remove&domain=store&locale=es-MX"

    json = {
        "operationName": "getStores",
        "variables": {},
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "471f622bb6d6b106a74e009f2bdd42176342c97f8026842c1d7730bfed53af6d",
                "sender": "vtex.store-locator@0.x",
                "provider": "vtex.store-locator@0.x",
            },
            "variables": "eyJmaWx0ZXJCeVRhZyI6Ik1hcmtldHBsYWNlIn0=",
        },
    }
    stores = session.post(base_link, headers=headers, json=json).json()["data"][
        "getStores"
    ]["items"]

    for store in stores:
        location_name = store["name"]
        addr = store["address"]
        street_address = (addr["street"] + " " + addr["number"]).strip()
        city = addr["city"]
        state = addr["state"]
        zip_code = addr["postalCode"]
        country_code = "Mexico"
        store_number = store["id"]
        phone = store["instructions"].replace("Tel.", "").strip()
        location_type = ""
        hours_of_operation = store["businessHours"]
        latitude = addr["location"]["latitude"]
        longitude = addr["location"]["longitude"]

        hours_of_operation = ""
        raw_hours = store["businessHours"]
        for hours in raw_hours:
            day = hours["dayOfWeek"]
            if day == 0:
                day = "Sunday"
            if day == 1:
                day = "Monday"
            if day == 2:
                day = "Tuesday"
            if day == 3:
                day = "Wednesday"
            if day == 4:
                day = "Thursday"
            if day == 5:
                day = "Friday"
            if day == 6:
                day = "Saturday"
            opens = hours["openingTime"]
            closes = hours["closingTime"]
            clean_hours = day + " " + opens + "-" + closes
            hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

        link = "https://www.partycity.com.mx/store/" + (
            location_name + "-" + state + "-" + zip_code + "/" + store_number
        ).lower().replace(" ", "-").replace("é", "e")
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
