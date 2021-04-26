from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("circle-a")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://circle-a.com/"
    base_url = "https://circle-a.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        addr = list(soup.select("p.indentp")[1].stripped_strings)
        yield SgRecord(
            page_url=base_url,
            location_name="Circle A - Fleet Fueling Solutions",
            street_address=addr[0],
            city=addr[1].split(",")[0].strip(),
            state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
            zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
            country_code="US",
            phone=list(soup.blockquote.stripped_strings)[1],
            locator_domain=locator_domain,
        )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
