from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.agm.at/api/stores/all"
    r = session.get(api, headers=headers)
    js = r.json()["groupedStores"]["VX"]

    for j in js:
        street_address = j.get("street")
        city = j.get("city")
        postal = j.get("zip")
        country_code = "AT"
        store_number = j.get("storeId")
        location_name = "AGM"
        page_url = f"https://www.agm.at/store/{store_number}"
        phone_code = j.get("telephoneAreaCode")
        phone_number = j.get("telephoneNumber")
        phone = f"{phone_code} {phone_number}".strip()
        latitude = j.get("yCoordinates")
        longitude = j.get("xCoordinates")
        hours_of_operation = j.get("openingTimesHTML")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.agm.at/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "lat": "48.2064956",
        "lon": "16.3755594",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.agm.at/maerkte",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
