from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("hightechburrito")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "http://hightechburrito.com/"
    base_url = "http://hightechburrito.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("table tr td")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.text.strip():
                continue
            addr = [_.text.strip() for _ in link.select("a") if _.text.strip()]
            yield SgRecord(
                page_url=base_url,
                location_name=link.strong.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[2],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
