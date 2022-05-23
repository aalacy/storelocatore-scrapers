from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests.sgrequests import SgRequests

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Host": "www.dealz.ie",
    "Referer": "https://www.dealz.ie/store-finder/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dealz.ie"
base_url = "https://www.dealz.ie/rest/dealz/V1/locator/?searchCriteria%5Bscope%5D=store-locator&searchCriteria%5Blatitude%5D=51.9143321&searchCriteria%5Blongitude%5D=-8.1726276&searchCriteria%5Bcurrent_page%5D=1&searchCriteria%5Bpage_size%5D=1000"


def fetch_records(http):
    locations = http.get(base_url, headers=_headers).json()["locations"]

    for _ in locations:
        addr = _["address"]
        hours = []
        for hh in _["opening_hours"]:
            hours.append(f"{hh['day']}: {hh['hours']}")
        page_url = (
            f"https://www.dealz.ie/store-finder/store_page/view/id/{_['store_id']}/"
        )
        street_address = addr["line"]
        if type(addr["line"]) == list:
            street_address = " ".join(addr["line"])
        latitude = _["geolocation"]["latitude"]
        longitude = _["geolocation"]["longitude"]
        if latitude == "0.00000000":
            latitude = ""
        if longitude == "0.00000000":
            longitude = ""
        phone = _["tel"]
        if phone:
            phone = phone.split("/")[0].strip()
        if addr["postcode"] and addr["postcode"].replace("-", "").isdigit():
            continue
        yield SgRecord(
            page_url=page_url,
            location_name=_["name"],
            store_number=_["store_id"],
            street_address=street_address,
            city=addr["city"],
            zip_postal=addr["postcode"],
            country_code=addr["country"],
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
        )


if __name__ == "__main__":
    with SgRequests() as http:
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=10
            )
        ) as writer:
            for rec in fetch_records(http):
                writer.write_row(rec)
