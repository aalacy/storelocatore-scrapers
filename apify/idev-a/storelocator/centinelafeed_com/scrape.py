from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa
import json

locator_domain = "https://centinelafeed.com/"
base_url = "https://centinela-feed.herokuapp.com/api/v1/cf-db/stores/get-stores"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://centinelafeed.com/",
        "Origin": "https://centinelafeed.com",
    }


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers())
        locations = json.loads(res.text)["data"]
        for _ in locations:
            hours = []
            for key, val in _["hours"].items():
                hours.append(f"{key}: {val}")
            hours_of_operation = "; ".join(hours)
            addr = parse_address_usa(_["address"])
            yield SgRecord(
                store_number=_["_id"],
                location_name=_["name"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
