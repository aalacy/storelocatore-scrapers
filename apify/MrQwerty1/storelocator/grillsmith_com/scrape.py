from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.grillsmith.com/graphql"
    r = session.post(api, headers=headers, json=json_data)
    js = r.json()["data"]["restaurant"]["locations"]

    for j in js:
        street_address = j.get("streetAddress") or ""
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postalCode")
        country_code = "US"
        store_number = j.get("id")
        location_name = j.get("name")
        slug = j.get("slug") or ""
        slug = slug.replace("grillsmith-", "")
        page_url = f"https://www.grillsmith.com/{slug}"
        phone = j.get("displayPhone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        hours = j.get("schemaHours") or ["Closed"]
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.grillsmith.com/"
    headers = {"Referer": "https://www.grillsmith.com/"}
    json_data = {
        "operationName": "restaurantWithLocations",
        "variables": {
            "restaurantId": 12002,
        },
        "extensions": {
            "operationId": "PopmenuClient/94a9b149c729821816fee7d97a05ecac",
        },
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
