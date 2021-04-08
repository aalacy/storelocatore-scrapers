from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "http://www.tote-a-poke.com/"
    base_url = "http://www.tote-a-poke.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul.et_pb_tabs_controls li")
        for link in locations:
            _ = soup.select_one(f"div.et_pb_all_tabs .{link['class'][0]} a")
            address = _.img["alt"]
            if not address or address == "Tote-A-Poke":
                address = _["href"].split("place/")[1].split("/@")[0].replace("+", " ")
            if address == "Tote-A-Poke":
                address = link.text
            addr = parse_address_intl(address)
            coord = _["href"].split("/@")[1].split(",17z/data")[0].split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=link.text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=addr.postcode,
                country_code="US",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
