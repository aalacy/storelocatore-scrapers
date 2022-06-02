from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=200
    )
    for lat, lng in search:
        api = f"https://www.timpson.co.uk/storefinder/locator/get/{lat}/{lng}/1"
        r = session.post(api, headers=headers, data=data)
        js = r.json()["locations"]

        for j in js:
            page_url = f'https://www.timpson.co.uk/stores/{j.get("url")}'
            location_name = j.get("name")
            street_address = j.get("street1")
            city = j.get("city")
            postal = j.get("zip")
            store_number = j.get("store_no")
            phone = j.get("phone")
            latitude = j.get("lat")
            longitude = j.get("lng")

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

            for i in range(1, 8):
                time = j.get(f"opening_{i}")
                day = days[i - 1]
                _tmp.append(f"{day}: {time}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code="GB",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.timpson.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.timpson.co.uk/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.timpson.co.uk",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    data = {"start": "1000"}
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
