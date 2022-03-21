from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://wingatehealthcare.com"
base_url = "https://wingatehealthcare.com/wp-content/themes/wingate/data-locations.json"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["locations"]
        for _ in locations:
            yield SgRecord(
                page_url=_["link"],
                store_number=_["ID"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zipcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["phone"].split("|")[0].strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
