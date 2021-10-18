from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dormezvous.com"
base_url = "https://www.dormezvous.com/ccstorex/custom/v1/stores/?locale=en"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["result"]
        for _ in locations:
            street_address = _["address1"]
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in bs(_["hours"], "lxml").select("table tr")
            ]
            yield SgRecord(
                page_url="https://www.dormezvous.com/en/storelocator",
                store_number=_["externalLocationId"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["stateAddress"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"] or "CA",
                phone=_.get("phoneNumber"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
