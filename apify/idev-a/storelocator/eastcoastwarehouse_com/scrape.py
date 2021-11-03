from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("eastcoastwarehouse")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://eastcoastwarehouse.com"
base_url = "https://eastcoastwarehouse.com/contact/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = (
            soup.find("b", string=re.compile(r"Warehouse"))
            .find_parent()
            .find_next_siblings("p")[2:]
        )
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.text.strip():
                continue
            addr = list(link.stripped_strings)
            if "@" in addr[-1]:
                del addr[-1]
            if len(addr) == 1:
                continue
            if len(addr) <= 3 and "Phone" in "".join(addr):
                continue
            try:
                coord = link.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=addr[0],
                street_address=addr[1],
                city=addr[2].split(",")[0].strip(),
                state=addr[2].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[2].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
