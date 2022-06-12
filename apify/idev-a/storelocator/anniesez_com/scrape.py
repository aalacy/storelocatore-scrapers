from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.calranch.com/"
        base_url = "http://www.anniesez.com/stores.html"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("table table tr")[1:]
        for _ in locations:
            td = _.select("td")
            yield SgRecord(
                page_url=base_url,
                location_name=td[4].text.strip(),
                street_address=td[0].text.strip(),
                city=td[1].text.strip(),
                state=td[2].text.strip(),
                zip_postal=td[3].text.strip(),
                country_code="US",
                phone=td[5].text.strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
