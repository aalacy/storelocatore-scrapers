from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("wowlogistics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://wowlogistics.com"
base_url = "https://wowlogistics.com/our-locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.flexcontainer.col1 div.location-popup")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(link.select_one(".center p").stripped_strings)
            coord = (
                link.iframe["src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3m")[0]
                .split("!3d")
            )
            yield SgRecord(
                page_url=base_url,
                location_name=f"{link.h2.text.strip().split('–')[0]} {link.select_one('.title p').text.strip()}",
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[2],
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
