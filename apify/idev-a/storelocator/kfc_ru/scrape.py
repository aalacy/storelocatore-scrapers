from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "origin": "https://www.kfc.ru",
    "referer": "https://www.kfc.ru/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

payload = {
    "coordinates": [55.77500599999999, 37.583211000000006],
    "radiusMeters": 100000,
    "channel": "website",
}

locator_domain = "https://www.kfc.ru"
base_url = "https://api.kfc.com/api/store/v2/store.geo_search"


def fetch_data():
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers, json=payload).json()[
            "searchResults"
        ]
        for store in locations:
            _ = store["store"]
            addr = _["contacts"]
            location_type = ""
            if not _["openNow"]:
                location_type = "closed"
            hours = []
            for hh in _["openingHours"]["regularDaily"]:
                hours.append(f"{hh['weekDayName']}: {hh['timeFrom']}-{hh['timeTill']}")
            yield SgRecord(
                page_url="https://www.kfc.ru/restaurants",
                store_number=_["storeId"],
                location_name=_["title"]["en"],
                street_address=addr.get("streetAddress", {}).get("en"),
                city=addr.get("city", {}).get("en"),
                latitude=addr["coordinates"]["geometry"]["coordinates"][0],
                longitude=addr["coordinates"]["geometry"]["coordinates"][1],
                country_code="Ru",
                location_type=location_type,
                phone=addr["phoneNumber"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
