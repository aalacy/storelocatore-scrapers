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

locator_domain = "https://www.kfc.ru"
base_url = "https://api.kfc.com/api/store/v2/store.get_restaurants"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["searchResults"]
        for x, store in enumerate(locations):
            _ = store["storePublic"]
            addr = _["contacts"]
            raw_address = addr.get("streetAddress", {}).get("ru")
            if not raw_address:
                continue
            if _["status"] != "Open":
                continue
            hours = []
            if _["openingHours"]["regularDaily"]:
                for hh in _["openingHours"]["regularDaily"]:
                    hours.append(
                        f"{hh['weekDayName']}: {hh['timeFrom']}-{hh['timeTill']}"
                    )
            zip_postal = raw_address.split(",")[0].strip()
            if not zip_postal.isdigit():
                zip_postal = ""
            street_address = raw_address

            if zip_postal:
                street_address = ", ".join(raw_address.split(",")[1:])

            city = addr.get("city", {}).get("ru")
            if city and city in street_address:
                street_address = ", ".join(street_address.split(",")[1:])
            yield SgRecord(
                page_url="https://www.kfc.ru/restaurants",
                store_number=_["storeId"],
                location_name=_["title"]["ru"],
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                latitude=addr["coordinates"]["geometry"]["coordinates"][0],
                longitude=addr["coordinates"]["geometry"]["coordinates"][1],
                country_code="Ru",
                location_type=_["status"],
                phone=addr["phoneNumber"].split("доб")[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
