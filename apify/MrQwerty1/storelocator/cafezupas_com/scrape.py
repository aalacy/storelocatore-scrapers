from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://cafezupas.com/server.php?url=https://api.controlcenter.zupas.com/api/markets/listing"
    r = session.get(api)
    locations = r.json()["data"]["data"]

    for location in locations:
        js = location["locations"]
        for j in js:
            street_address = j.get("address")
            city = j.get("city")
            state = j.get("state")
            postal = j.get("zip")
            store_number = j.get("id")
            location_name = j.get("name")
            phone = j.get("phone")
            latitude = j.get("lat")
            longitude = j.get("long")

            _tmp = []
            if j.get("mon_thurs_timings_open"):
                _tmp.append(
                    f'Mon-Thu: {j.get("mon_thurs_timings_open")} - {j.get("mon_thurs_timings_close")}'
                )
            else:
                _tmp.append(f'Mon-Thu: {j.get("mon_thurs_timings")}')

            if j.get("fri_sat_timings_open"):
                _tmp.append(
                    f'Fri-Sat: {j.get("fri_sat_timings_open")} - {j.get("fri_sat_timings_close")}'
                )
            else:
                _tmp.append(f'Fri-Sat: {j.get("fri_sat_timings")}')

            if j.get("sunday_timings"):
                _tmp.append(f'Sun: {j.get("sunday_timings")}')

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                location_name=location_name,
                page_url=page_url,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://cafezupas.com/"
    page_url = "https://cafezupas.com/locations"
    session = SgRequests()

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
