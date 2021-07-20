from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re
import json

logger = SgLogSetup().get_logger("razzoos")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.razzoos.com"
base_url = "https://www.razzoos.com/find-us"


def _p(val):
    return (
        val.replace("(", "")
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
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("main div.summary-item-list div.summary-item")
        logger.info(f"{len(links)} found")
        for link in links:
            if "Coming" in link.text:
                continue
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            ss = json.loads(
                sp1.select_one("div.sqs-block-map")["data-block-json"]
                .replace("&#123;", "{")
                .replace("&#125;", "}")
                .replace("&quot;", '"')
            )
            _addr = []
            for aa in link.select_one("div.summary-excerpt p").stripped_strings:
                if "Phone" in aa:
                    break
                if "(" in aa or ")" in aa:
                    continue
                _addr.append(aa)
            addr = parse_address_intl(" ".join(_addr))
            street_address = _addr[0]
            if addr.postcode in street_address:
                street_address = street_address.split(addr.city)[0].strip()

            phone = ""
            if link.find("a", href=re.compile(r"tel:")):
                phone = link.find("a", href=re.compile(r"tel:")).text.strip()
            if not phone and sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=link.select_one("div.summary-title").text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=ss["location"]["mapLat"],
                longitude=ss["location"]["mapLng"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
