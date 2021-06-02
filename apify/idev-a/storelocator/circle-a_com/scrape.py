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
    base_url = "https://www.circle-a.com/locations.php"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul li a")
        logger.info(f"{len(locations)} founds")
        for _ in locations:
            page_url = locator_domain + _["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            location_name = sp1.select("table tr td table tr td  table tr td")[
                1
            ].text.strip()
            block = list(
                sp1.select("table tr td table tr td  table tr td")[3].stripped_strings
            )
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=block[-3],
                city=block[-2].split(",")[0].strip(),
                state=block[-2].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=block[-2].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=block[-1],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
