from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.valentine.ca"
    base_url = "https://www.valentine.ca/en/location"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.addresses article.address")
        for _ in locations:
            page_url = locator_domain + _.select_one("h3.location_title a")["href"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = parse_address_intl(soup1.select_one("div.card-address").text)
            coord = json.loads(_["data-position"])
            yield SgRecord(
                page_url=page_url,
                store_number=_["data-id"],
                location_name=_.select_one("h3.location_title a")["data-gtm"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                latitude=coord["lat"],
                longitude=coord["lng"],
                zip_postal=addr.postcode,
                country_code="CA",
                phone=_.select_one("a.bt_phone").text,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
