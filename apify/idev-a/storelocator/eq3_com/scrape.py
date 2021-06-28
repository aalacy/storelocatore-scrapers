from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.eq3.com/"
    base_url = "https://api.eq3.com/locations?locale=US_EN"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            if _["address"]["country"] not in ["US", "CA"]:
                continue
            page_url = f"https://www.eq3.com/us/en/shopwithus/eq3-locations/{_['id']}/{_['address']['city']}/{_['slug']}"
            hours = []
            for hh in _["hours"]["store"]:
                time = "closed"
                if not hh["isClosed"]:
                    time = f"{hh['opening']}-{hh['closing']}"
                hours.append(f"{hh['day']}: {time}")
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"]["streetAddress"],
                city=_["address"]["city"],
                state=_["address"]["province"],
                latitude=_["lat"],
                longitude=_["lng"],
                zip_postal=_["address"]["postalCode"],
                country_code=_["address"]["country"],
                location_type=_["type"],
                phone=_["address"]["phoneNumbers"][0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
