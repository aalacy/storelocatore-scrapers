from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.99restaurants.com/"
    base_url = "https://orderback.99restaurants.com:8081/restaurants?radius=500"
    page_url = "https://order.99restaurants.com/?location=true&locationId={}"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["restaurants"]:
            hh = _["calendars"][0]["ranges"][0]
            hours_of_operation = f"{hh['weekday']}: {hh['start'].split(' ')[-1]}-{hh['end'].split(' ')[-1]}"
            yield SgRecord(
                page_url=page_url.format(_["id"]),
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["streetaddress"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
