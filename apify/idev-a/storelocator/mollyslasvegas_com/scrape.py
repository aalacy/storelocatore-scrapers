from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl


logger = SgLogSetup().get_logger("mollyslasvegas")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "http://mollyslasvegas.com"
    base_url = "http://mollyslasvegas.com/find-a-mollys-near-you/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.entry-content ul li")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            _addr = list(_.h2.stripped_strings)[1:-1]
            addr = parse_address_intl(" ".join(_addr))
            street_address = " ".join(_addr[:-2])
            yield SgRecord(
                page_url=base_url,
                store_number=_["data-store-id"],
                location_name=_.h2.strong.text.replace("’", "'").strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
