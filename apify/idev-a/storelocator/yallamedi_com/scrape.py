from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "referer": "https://locations.yallamedi.com/search",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://yallamedi.com/"
    base_url = "https://locations.yallamedi.com/search?country=us&per=50"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for loc in locations["locations"]:
            _ = loc["loc"]
            street_address = _["address1"]
            if _["address2"]:
                street_address += ", " + _["address2"]
            hours = []
            for hh in _["hours"]["days"]:
                time = f"{hh['intervals'][0]['start']}-{hh['intervals'][0]['end']}"
                hours.append(f"{hh['day']}: {time}")
            yield SgRecord(
                page_url=_["website"]["url"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                zip_postal=_["postalCode"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
