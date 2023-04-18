from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://villamadina.com/"
    base_url = "https://api.storerocket.io/api/user/E5Z4wBKpPd/locations?radius=50&units=kilometers"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["results"]["locations"]:
            street_address = " ".join(_["display_address"].split(",")[:-3])
            hours = []
            for day, hh in _["hours"].items():
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url="https://villamadina.com/locations",
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postcode"],
                location_type=_["location_type_name"],
                country_code=_["country"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
