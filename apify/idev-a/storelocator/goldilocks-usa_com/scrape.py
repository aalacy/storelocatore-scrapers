from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("goldilocks")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.goldilocks-usa.com/"
    base_url = "https://www.goldilocks-usa.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("#tab1 div.tab-content div.tab-pane")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            addr = list(_.select_one(".map-info ul li").stripped_strings)
            try:
                coord = _.iframe["src"].split("!2d")[1].split("!3m")[0].split("!3d")
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=_.find("a", href=re.compile(r"tel:")).text.strip(),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(
                    list(_.select(".map-info")[1].stripped_strings)[1:]
                ).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
