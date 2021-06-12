from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.altamed.org/"
    base_url = "https://www.altamed.org/find/resultsJson?type=clinic&affiliates=yes"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["items"]:
            addr = parse_address_intl(_["address"])
            yield SgRecord(
                page_url="https://www.altamed.org/find/results?type=clinic&keywords=85281&affiliates=yes",
                location_name=_["name"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lon"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_["den_work_hour"].replace(",", ";"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
