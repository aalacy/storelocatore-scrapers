from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.mackage.com/"
    base_url = "https://www.mackage.com/us/en/store-locator?load=true"
    with SgRequests() as session:
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = json.loads(
            sp1.select_one("div.storeJSON")["data-storejson"]
            .replace("&quot;", '"')
            .replace("&#40;", "(")
            .replace("&#41;", ")")
        )
        for _ in locations:
            country_code = _["countryCode"]
            state = _["stateCode"]
            if not country_code:
                addr = parse_address_intl(
                    f"{_['address1']}, {_['address2']}, {_['city']}, {_['stateCode']}"
                )
                if addr.country:
                    country_code = addr.country
                state = addr.state
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            yield SgRecord(
                page_url=base_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=state,
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=country_code,
                phone=_["phone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
