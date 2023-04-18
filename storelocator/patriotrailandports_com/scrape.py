from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("patriotrailandports")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://patriotrailandports.com"
base_url = "https://patriotrailandports.com/about-us/network-map/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul.posts-list-wrapper li.gmw-single-item")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.h2.a["href"]
            addr = link.select_one("div.address-wrapper a").text.strip().split(",")
            coord = (
                link.select_one("a.gmw-get-directions")["href"]
                .split("daddr=")[1]
                .split("&")[0]
                .split(",")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=link.h2.text.strip(),
                street_address=addr[0],
                city=addr[1].strip(),
                state=addr[2].strip().split(" ")[0].strip(),
                zip_postal=addr[2].strip().split(" ")[1].strip(),
                country_code="US",
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
