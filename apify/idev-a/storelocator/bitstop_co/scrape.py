from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://bitstop.co"
base_url = "https://bitstop.co/get-atms"


def _state(abbr):
    state = "puerto rico"
    for ss in us.states.STATES:
        if ss.abbr == abbr:
            state = ss.name.lower()
            break
    return state


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["street_address"]
            _city = _["city"].replace(" ", "-").lower()
            page_url = f"https://bitstop.co/{_state(_['state']).replace(' ','-')}/{_city}/{_['slug']}-{_city}-bitcoin-atm"
            country_code = _["country"]
            if country_code == "TX":
                country_code = "US"
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zipcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=country_code,
                phone=_["phone"],
                location_type="atm",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(_["hours"]),
                raw_address=_["full_address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
