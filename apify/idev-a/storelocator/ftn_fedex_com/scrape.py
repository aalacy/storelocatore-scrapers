from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from urllib.parse import urljoin
from sgscrape.sgpostal import parse_address_intl
from sgselenium import SgChrome
import time
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
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
        .replace("Air", "")
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
                                    .replace("phone", "")
                                    .split(",")[0]
                                    .split("ext")[0]
                                    .split("&")[0]
                                    .split("/")[0]
                                    .split("(air")[0]
                                    .strip()
                                )
                                if "phone" in bb.lower() and _p(phone):
                                    _addr = blocks[1:x]
                                    break
                                else:
                                    phone = ""
                            temp = []
                            for aa in _addr:
                                if (
                                    "FedEx" in aa
                                    or "corporation" in aa.lower()
                                    or "posta" in aa.lower()
                                    or "company" in aa.lower()
                                    or "ltd" in aa.lower()
                                    or "llc" in aa.lower()
                                    or "international center" in aa.lower()
                                    or "fortune center" in aa.lower()
                                ):
                                    continue
                                temp.append(aa)
                            _addr = temp
                            street_address = state = city = zip_postal = ""
                            if _addr:
                                _address = ", ".join(_addr)
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
                                city = addr.city
                                zip_postal = addr.postcode
                                if zip_postal == "00000":
                                    zip_postal = ""
                            if (
                                country_code == "Indonesia"
                                or country_code == "Angola"
                                or country_code == "Egypt"
                                or country_code == "Ghana"
                                or country_code == "Madagascar"
                                or country_code == "Morocco"
                                or country_code == "Mozambique"
                                or country_code == "Australia"
                                or country_code == "Bangladesh"
                                or country_code == "Hong Kong"
                                or country_code == "Singapore"
                                or country_code == "Austria"
                                or country_code == "Finland"
                                or country_code == "Greece"
                                or country_code == "Ireland"
                                or country_code == "Norway"
                                or country_code == "Portugal"
                                or country_code == "Sweden"
                                or country_code == "Jordan"
                                or country_code == "Lebanon"
                                or country_code == "Chile"
                                or country_code == "Colombia"
                                or country_code == "Costa Rica"
                                or country_code == "Ecuador"
                                or country_code == "El Salvador"
                                or country_code == "Guatemala"
                                or country_code == "Nicaragua, Peru"
                            ):
                                city = blocks[0]
                            if (
                                country_code == "Indonesia"
                                and blocks[0] == "Seoul"
                                or country_code == "Malaysia"
                                and blocks[0] == "Penang"
                                or country_code == "Philippines"
                                and blocks[0] == "Cebu"
                                or country_code == "India"
                                and blocks[0] == "Bangalore"
                                or country_code == "India"
                                and blocks[0] == "Chennai"
                                or country_code == "UAE"
                                and blocks[0] == "Dubai"
                                or country_code == "Argentina"
                                and blocks[0] == "Ezeiza"
                                or country_code == "Bolivia"
                                and blocks[0] == "Cochabamba"
                            ):
                                city = blocks[0]
                            yield SgRecord(
                                page_url=page_url,
                                location_name=blocks[0],
                                street_address=street_address,
                                city=city,
                                state=state,
                                zip_postal=zip_postal,
                                country_code=country_code,
                                phone=phone,
                                locator_domain=locator_domain,
                            )

                        break


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
