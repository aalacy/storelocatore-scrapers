from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cultures-restaurants.com"
page_url = "https://www.cultures-restaurants.com/locations"
base_url = "https://api.storerocket.io/api/user/0kDJ39Qpmn/locations?radius=20&units=kilometers"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["results"][
            "locations"
        ]
        for _ in locations:
            street_address = _["address"].split(",")[0]
            if _["address_line_2"]:
                street_address += " " + _["address_line_2"]
            hours = []
            for day, hh in _["hours"].items():
                if hh:
                    hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postcode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                location_type=_["location_type_name"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
