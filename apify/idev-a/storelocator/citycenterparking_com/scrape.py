from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ccplots.myparkingworld.com"
base_url = "https://ccplots.myparkingworld.com/api/lots/CCP/EN?latLoc=45.5230622&lngLoc=-122.6764816&latCenter=45.5230622&lngCenter=-122.6764816&csr=0&branchName="


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = _["address"]
            street_address = addr["address1"]
            if addr["address2"]:
                street_address += " " + addr["address2"]
            page_url = f"https://ccplots.myparkingworld.com/CCP/en?latlng=45.5230622,-122.67648159999999&_ga=2.90973594.1063415383.1632952321-737608664.1632952321#details=61,{_['lotNumber']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["lotNumber"],
                location_name=_["lotName"],
                street_address=street_address,
                city=addr["city"],
                state=addr["provState"],
                zip_postal=addr["postalCode"],
                latitude=_["location"]["lat"],
                longitude=_["location"]["lng"],
                country_code=addr["country"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
