from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from urllib.parse import urljoin
from sgscrape.sgpostal import parse_address_intl
from sgselenium import SgChrome
import time

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("fedex")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ftn.fedex.com"
base_url = "https://ftn.fedex.com/us/locations/"
json_url = "https://ftn.fedex.com/agents/LocationServer.jsp?x=x&country="


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
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("ul#nav-local a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = urljoin(locator_domain, link["href"])
            if not page_url.startswith("http"):
                page_url = locator_domain + page_url
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
                            _addr = []
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
                                    _addr = blocks[:x]
                                    break
                                else:
                                    phone = ""
                            temp = []
                            for aa in _addr:
                                if (
                                    "FedEx" in aa
                                    or "corporation" in aa.lower()
                                    or "company" in aa.lower()
                                    or "ltd" in aa.lower()
                                    or "llc" in aa.lower()
                                    or "center" in aa.lower()
                                ):
                                    continue
                                temp.append(aa)
                            _addr = temp
                            street_address = state = zip_postal = ""
                            if _addr:
                                _address = " ".join(_addr)
                                addr = parse_address_intl(_address)
                                street_address = addr.street_address_1
                                if addr.street_address_2:
                                    street_address += " " + addr.street_address_2
                                if (
                                    street_address
                                    and street_address.replace("-", "").isdigit()
                                ):
                                    for aa in _addr:
                                        if aa.startswith(street_address):
                                            street_address = aa
                                            break
                                state = addr.state
                                zip_postal = addr.postcode
                                if zip_postal == "00000":
                                    zip_postal = ""
                            yield SgRecord(
                                page_url=page_url,
                                location_name=blocks[0],
                                street_address=street_address,
                                city=blocks[0],
                                state=state,
                                zip_postal=zip_postal,
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
