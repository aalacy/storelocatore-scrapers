from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.whsmith.co.uk/mobify/proxy/api/s/whsmith/dw/shop/v21_3/stores"

    for i in range(0, 5000, 200):
        params = (
            ("latitude", "57.28687230000001"),
            ("longitude", "-2.3815684"),
            ("distance_unit", "mi"),
            ("country_code", "GB"),
            ("max_distance", "3000.00"),
            ("count", "200"),
            ("start", f"{i}"),
        )
        r = session.get(api, headers=headers, params=params)
        js = r.json()["data"]

        for j in js:
            location_name = j.get("name")
            store_number = j.get("id")
            location_type = j.get("_type")
            page_url = (
                f"https://www.whsmith.co.uk/stores/details/?StoreID={store_number}"
            )
            street_address = f'{j.get("address1")} {j.get("address2") or ""}'.strip()
            city = j.get("city")
            state = j.get("state_code")
            postal = j.get("postal_code")
            country_code = "GB"
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            _tmp = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            for day in days:
                inter = j.get(f"c_openingTimes{day}")
                if "closed" in inter:
                    _tmp.append(f"{day}: Closed")
                    continue
                _tmp.append(f"{day}: {inter}")
            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 200:
            break


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.whsmith.co.uk/"
    headers = {
        "x-dw-client-id": "7d637d46-28d8-44c4-b652-5eabde15e19e",
    }

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
