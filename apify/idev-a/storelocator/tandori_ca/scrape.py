from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "http://tandori.ca/"
    base_url = "http://tandori.ca/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(".elementor-element.elementor-col-33")
        for _ in locations:
            if not _.select_one("h2.elementor-heading-title"):
                continue
            location_name = _.select_one("h2.elementor-heading-title").text
            block = list(_.select_one("div.elementor-text-editor").stripped_strings)
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=block[0],
                city=block[1].split(",")[0].strip(),
                state=block[1].split(",")[1].strip().split(" ")[0],
                zip_postal=" ".join(block[1].split(",")[1].strip().split(" ")[1:]),
                country_code="CA",
                phone=block[-1],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
