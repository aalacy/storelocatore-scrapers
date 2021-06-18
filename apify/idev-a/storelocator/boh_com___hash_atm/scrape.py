from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.boh.com/"
    page_url = "https://www.boh.com/locations"
    base_url = "https://www.boh.com/get-locations?lat=21.33&lng=-157.845934&radius=5000"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["locations"]:
            street_address = _["address"]["address1"]
            if _["address"]["address2"]:
                street_address += " " + _["address"]["address2"]
            addr = parse_address_intl(
                f'{_["address"]["city"]} {_["address"]["state"]} {_["address"]["zip"]}'
            )
            hours = []
            for day, times in _["operationalHours"]["hours"].items():
                if times["isClosed"]:
                    hh = "closed"
                else:
                    hh = f"{times['hours'][0]['openTime']}-{times['hours'][0]['closeTime']}"
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["displayName"].replace("–", "-"),
                location_type=", ".join(_["type"]),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["geocode"]["latitude"],
                longitude=_["geocode"]["longitude"],
                country_code="US",
                phone=_["phone"] if _["phone"] else "",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
