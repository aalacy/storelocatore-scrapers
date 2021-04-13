from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("symposiumcafe")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://symposiumcafe.com/"
    base_url = "https://symposiumcafe.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul.three-columns-list li a")
        for link in links:
            logger.info(link["href"])
            sp1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            addr = " ".join(
                list(sp1.select_one("address").stripped_strings)[:-4]
            ).split(",")
            coord = (
                sp1.select_one("div.widget iframe")["src"]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!2m")[0]
                .split("!3d")
            )
            yield SgRecord(
                page_url=link["href"],
                location_name=link.text,
                street_address=addr[0].replace(",", ""),
                city=addr[1],
                state=addr[2].strip().split(" ")[0],
                latitude=coord[1],
                longitude=coord[0],
                zip_postal=" ".join(addr[2].strip().split(" ")[-2:]),
                country_code="CA",
                phone=sp1.find("a", href=re.compile(r"tel:")).text,
                locator_domain=locator_domain,
                hours_of_operation=": ".join(
                    sp1.select_one("div.widget time").stripped_strings
                ).replace("\n", ""),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
