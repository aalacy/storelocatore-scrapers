from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.ampol.com.au/custom/api/locator/get?filter=((Channel%20eq%20%27FOODARY%27))"
    r = session.get(api, headers=headers)
    js = r.json()["value"]

    for j in js:
        location_name = j.get("DisplayName")
        street_address = j.get("Address")
        city = j.get("Suburb")
        state = j.get("State")
        postal = j.get("Postcode")
        country_code = "AU"
        store_number = j.get("LocationID")
        location_type = j.get("Channel")
        phone = j.get("Phone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")

        _tmp = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            start = j.get(f"{day}_Openning")
            end = j.get(f"{day}_Closing")
            if start and start == end:
                _tmp.append(f"{day}: 24 hours")
            elif start:
                _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)
        if hours_of_operation.count("24 hours") == 7:
            hours_of_operation = "24/7"

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
            location_type=location_type,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.ampol.com.au/"
    page_url = "https://www.ampol.com.au/service-stations/find-a-service-station?services=FOODARY"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
