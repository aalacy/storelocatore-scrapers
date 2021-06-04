from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("oldpoint")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://oldpoint.com/"
    base_url = "https://oldpoint.com/our-services/bank/investing/branch-locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.accordion div.accordion-content")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(
                link.find("strong", string=re.compile(r"Address:"))
                .find_parent("p")
                .stripped_strings
            )[1].split(",")
            phone = ""
            if link.find("strong", string=re.compile(r"Phone:")):
                phone = list(
                    link.find("strong", string=re.compile(r"Phone:"))
                    .find_parent("p")
                    .stripped_strings
                )[1]
            hours_of_operation = ""
            if link.find("strong", string=re.compile(r"Lobby Hours:")):
                hours_of_operation = list(
                    link.find("strong", string=re.compile(r"Lobby Hours:"))
                    .find_parent("p")
                    .stripped_strings
                )[1]
            try:
                yield SgRecord(
                    page_url=base_url,
                    location_name=link.h3.text.strip(),
                    raw_address=", ".join(addr),
                    street_address=addr[0],
                    city=addr[1].strip(),
                    state=addr[2].strip().split(" ")[0].strip(),
                    zip_postal=addr[2].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
