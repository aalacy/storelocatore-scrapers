from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tippmanngroup")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.tippmanngroup.com"
base_url = "https://www.tippmanngroup.com/interstate-warehousing/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.themeblvd-gallery div.grid-item")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            addr = list(sp1.select_one("div.textwidget center").stripped_strings)
            coord = res.split("new google.maps.LatLng(")[1].split(")")[0].split(",")
            yield SgRecord(
                page_url=page_url,
                location_name=link.h2.text.strip().replace("–", "-"),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[2],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
