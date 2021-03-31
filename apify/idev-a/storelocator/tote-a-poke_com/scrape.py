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
        locations = soup.select(".et_pb_section.et_pb_section_1 .et_pb_row")
        for _ in locations[1:]:
            addr = parse_address_intl(_.p.text)
            coord = _.a["href"].split("!3d")[1].split("!4d")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h4.text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=addr.postcode,
                country_code=addr.country,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
