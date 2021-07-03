from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from urllib.parse import urljoin
from sgscrape.sgpostal import parse_address_intl
from sgselenium import SgChrome
import time

logger = SgLogSetup().get_logger("fedex")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://ftn.fedex.com"
base_url = "http://ftn.fedex.com/us/locations/"
json_url = "http://ftn.fedex.com/agents/LocationServer.jsp?x=x&country="


def _p(val):
    return (
        val.lower()
        .split("ext")[0]
        .split("/")[0]
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            links = soup.select("ul#nav-local a")
            logger.info(f"{len(links)} found")
            for link in links:
                page_url = urljoin(locator_domain, link["href"])
                logger.info(page_url)
                driver.get(page_url)
                exist = False
                while not exist:
                    time.sleep(1)
                    for rr in driver.requests[::-1]:
                        if rr.url.startswith(json_url) and rr.response:
                            exist = True
                            sp1 = bs(rr.response.body.strip(), "lxml")
                            country_code = ""
                            for _ in sp1.select("table td"):
                                blocks = list(_.stripped_strings)
                                if len(blocks) == 1:
                                    country_code = blocks[0]
                                    continue
                                addr = []
                                phone = ""
                                for x, bb in enumerate(blocks):
                                    phone = (
                                        bb.lower()
                                        .split(":")[-1]
                                        .replace("Phone", "")
                                        .split("ext")[0]
                                        .split("/")[0]
                                        .strip()
                                    )
                                    if _p(phone):
                                        addr = blocks[:x]
                                        break
                                    else:
                                        phone = ""
                                if not addr:
                                    addr = blocks

                                if "FedEx" in addr[0]:
                                    del addr[0]
                                addr = parse_address_intl(" ".join(addr[1:]))
                                street_address = addr.street_address_1
                                if addr.street_address_2:
                                    street_address += " " + addr.street_address_2
                                yield SgRecord(
                                    page_url=page_url,
                                    location_name=blocks[0],
                                    street_address=street_address,
                                    city=addr.city,
                                    state=addr.state,
                                    zip_postal=addr.postcode,
                                    country_code=country_code,
                                    phone=phone,
                                    locator_domain=locator_domain,
                                )

                            break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
