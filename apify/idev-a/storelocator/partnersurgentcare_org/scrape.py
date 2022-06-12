from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://urgentcare.massgeneralbrigham.org"
    base_url = "https://urgentcare.massgeneralbrigham.org/locationsdata"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for node in locations["nodes"]:
            _ = node["node"]
            page_url = locator_domain + bs(_["title_linked"], "lxml").a["href"]
            addr = parse_address_intl(
                " ".join(bs(_["Address"], "lxml").stripped_strings)
            )
            hours_of_operation = ""
            if _["Hours"]:
                hours_of_operation = " ".join(bs(_["Hours"], "lxml").stripped_strings)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            location_type = ""
            if "Temporarily Closed" in _["title"]:
                location_type = "Temporarily Closed"
            location_name = _["title"].split("-")[0]
            yield SgRecord(
                page_url=page_url,
                store_number=_["Nid"],
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["Phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
