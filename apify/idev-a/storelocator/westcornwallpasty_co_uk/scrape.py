from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://westcornwallpasty.co.uk"
base_url = (
    "https://api.westcornwallpasty.co.uk/wp-json/wp/v2/stores?per_page=100&_limit=-1"
)


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = _["acf"]["location"]
            street_address = addr["address_line_1"]
            if addr["address_line_2"]:
                street_address += " " + addr["address_line_2"]
            yield SgRecord(
                page_url=_["link"],
                store_number=_["id"],
                location_name=_["title"]["rendered"],
                street_address=street_address,
                city=addr["city"],
                zip_postal=addr["postcode"],
                latitude=addr["latitude"],
                longitude=addr["longitude"],
                country_code="UK",
                location_type=_["type"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
