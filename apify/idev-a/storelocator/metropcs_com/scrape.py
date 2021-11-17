from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.metrobyt-mobile.com"
base_url = "https://www.metrobyt-mobile.com/self-service-sigma-commerce/v1/store-locator?address=90011&store-type=All&min-latitude=33.71803392753623&max-latitude=34.297744072463765&min-longitude=-117.88115110943396&max-longitude=-118.63586809056603"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = _["location"]["address"]
            page_url = f"https://www.metrobyt-mobile.com/storelocator/{addr['addressRegion'].lower()}/{addr['addressLocality'].lower().replace(' ', '-')}/{addr['streetAddress'].lower().replace(' ', '-')}"
            hours = []
            for hh in _["openingHours"]:
                hours.append(f'{",".join(hh["days"])}: {hh["time"]}')
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=addr["streetAddress"],
                city=addr["addressLocality"],
                state=addr["addressRegion"],
                zip_postal=addr["postalCode"],
                latitude=_["location"]["latitude"],
                longitude=_["location"]["longitude"],
                country_code="US",
                phone=_["telephone"],
                location_type=_["type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
