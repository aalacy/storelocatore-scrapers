from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://localcoinatm.com"
base_url = "https://localcoinatm.com/api/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = _["location"]
            page_url = f"https://localcoinatm.com/bitcoin-atm/{addr['stateSlug']}/{addr['citySlug']}/{addr['slug']}/"
            hours = []
            for hh in list(bs(_["description"], "lxml").stripped_strings):
                hours.append(hh.split(";")[0])
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=addr["street"],
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["zip"],
                latitude=addr["latitude"],
                longitude=addr["longitude"],
                country_code=addr["country"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("\\n", "; ")
                .replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
