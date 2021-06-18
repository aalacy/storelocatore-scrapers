from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

payload = {
    "operationName": "Locations",
    "variables": {},
    "query": "query Locations {\n  viewer {\n    locations {\n      ...LocationItem\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment LocationItem on Location {\n  id\n  description\n  hours {\n    day\n    time\n    __typename\n  }\n  name\n  phone\n  address\n  state\n  mapUrl\n  email\n  imageUrls\n  __typename\n}\n",
}


def fetch_data():
    locator_domain = "https://b8ta.com/"
    base_url = (
        "https://b8ta.com/ecomm/graphql?x_retailer=b8ta&x_domain=placeholder.local"
    )
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers, json=payload).json()
        for _ in locations["data"]["viewer"]["locations"]:
            if "Dubai" in _["name"]:
                continue
            addr = parse_address_intl(" ".join(_["address"]))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            for hh in _["hours"]:
                if "Call for" in hh["day"]:
                    break
                if "Open till event" in hh["day"]:
                    break
                _hr = f"{hh['day']}"
                if hh["time"]:
                    _hr += f": {hh['time']}"
                hours.append(_hr)
            page_url = locator_domain + _["id"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
