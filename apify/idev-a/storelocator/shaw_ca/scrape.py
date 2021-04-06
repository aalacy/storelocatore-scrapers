from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.shaw.ca/"
base_url = "https://support.shaw.ca/t5/billing-account-articles/shaw-retail-locations/ta-p/5183#content-section-0"

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        tables = soup.select("div.tkb-content-box table")
        for table in tables:
            for _ in table.select("tr"):
                city = _.select("td")[0].p.text.strip()
                addr = [
                    " ".join(aa.stripped_strings)
                    for aa in _.select("td")[1].select("p")
                ]
                if "Located across" in addr[-1]:
                    del addr[-1]
                yield SgRecord(
                    page_url=base_url,
                    location_name=addr[0],
                    street_address=" ".join(addr[1:-1]),
                    city=city,
                    zip_postal=addr[-1],
                    country_code="CA",
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
