from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://saborcharlotte.com/"
    base_url = "https://saborcharlotte.com/api/v1/locations"
    page_url = "https://saborcharlotte.com/locations"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["location"]:
            hours = []
            for hh in _["hours"]["day"]:
                time = f"{hh['open']}-{hh['close']}"
                if hh["open"].lower() == "closed":
                    time = "closed"
                hours.append(f"{hh['name']}: {time}")
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                latitude=_["lat"],
                longitude=_["lng"],
                zip_postal=_["zip"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
