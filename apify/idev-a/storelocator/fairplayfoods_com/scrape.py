from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.fairplayfoods.com/"
    base_url = "https://api.freshop.com/1/stores?app_key=fairplay_foods&has_address=true&limit=-1&token=aa4bb1ad26bad1b22a64d9aa3efc3a8e"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["items"]:
            street_address = _["address_1"]
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                store_number=_["store_number"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_["hours_md"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
