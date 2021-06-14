from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("sclogistics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.sclogistics.com/"
    base_url = "https://www.sclogistics.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.marker")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(link.p.stripped_strings)
            if len(addr) == 1:
                addr = addr[0].split("\r\n")
            phone = ""
            if link.find("p", string=re.compile(r"phone", re.IGNORECASE)):
                phone = (
                    link.find("p", string=re.compile(r"phone", re.IGNORECASE))
                    .text.split(":")[-1]
                    .replace("Phone", "")
                    .strip()
                )
            zip_postal = addr[-1].split(",")[1].strip().split(" ")[-1].strip()
            if not zip_postal.replace("-", "").strip().isdigit():
                zip_postal = ""
            yield SgRecord(
                page_url=link.a["href"],
                location_name=link.h4.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=link["data-lat"],
                longitude=link["data-lng"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
