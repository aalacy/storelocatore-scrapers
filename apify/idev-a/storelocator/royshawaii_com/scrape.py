from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
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

logger = SgLogSetup().get_logger("royyamaguchi")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def is_phone(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://www.royyamaguchi.com"
    base_url = "https://www.royyamaguchi.com"
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div#restaurants div.sqs-layout h3 a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            hours = []
            addr_found = False
            raw_address = None
            _hr = sp1.find(
                "", string=re.compile(r"daily DINE-IN & CARRYOUT:", re.IGNORECASE)
            )
            if _hr:
                hours = _hr.find_parent().stripped_strings
            else:
                _hr = sp1.find(
                    "",
                    string=re.compile(r"Open for dine-in & Carryout", re.IGNORECASE),
                )
                if _hr:
                    if _hr.find_parent("h1"):
                        hours = list(
                            _hr.find_parent("h1").find_next_sibling().stripped_strings
                        )
                    else:
                        hours = list(
                            _hr.find_parent("h2").find_next_sibling().stripped_strings
                        )
                    if hours and "DINE-IN" in hours[0]:
                        del hours[0]
                else:
                    _hr = sp1.find(
                        "strong", string=re.compile(r"^MONDAY", re.IGNORECASE)
                    )
                    if _hr:
                        temp = list(_hr.find_parent().stripped_strings)
                        if len(temp) % 2 == 0:
                            for x in range(0, len(temp), 2):
                                hours.append(f"{temp[x]} {temp[x+1]}")
                    else:
                        _hr = sp1.find(
                            "strong", string=re.compile(r"^HOURS", re.IGNORECASE)
                        )
                        if _hr:
                            hours = (
                                _hr.find_parent().find_next_sibling().stripped_strings
                            )

            _hr = sp1.find("strong", string=re.compile(r"^HOURS:", re.IGNORECASE))
            if _hr:
                hours = []
                temp = list(_hr.find_parent().stripped_strings)
                if len(temp) > 1:
                    hours = temp[1].split("|")
                    addr_found = True
                    raw_address = _hr.find_parent().find_next_sibling().text.strip()
                    addr = parse_address_intl(raw_address)
                else:
                    for hh in _hr.find_parent().find_next_siblings():
                        if hh.name != "h2":
                            break
                        hours.append(hh.text.strip())

            _phone = sp1.find("", string=re.compile(r"call FOR", re.IGNORECASE))
            phone = ""
            if _phone:
                if _phone.find_parent("h3"):
                    phone = list(_phone.find_parent("h3").stripped_strings)[-1]
                elif _phone.find_parent("h2"):
                    phone = list(_phone.find_parent("h2").stripped_strings)[-1]

            if not addr_found:
                _addr = sp1.select_one("div.sidebar__inner p")
                addr = None
                if _addr:
                    _addr = list(
                        sp1.select_one("div.sidebar__inner p").stripped_strings
                    )

                    if not is_phone(_addr[0]):
                        _phone = sp1.select("div.sidebar__inner p")[1]
                        if is_phone(_phone.text.strip()):
                            phone = _phone.text.strip()
                            hours = [
                                hh.text.strip() for hh in _phone.find_next_siblings("p")
                            ]
                    else:
                        phone = _addr[0]
                        del _addr[0]
                    raw_address = " ".join(_addr)
                    addr = parse_address_intl(raw_address)
                else:
                    _addr = sp1.find(
                        "strong", string=re.compile(r"address", re.IGNORECASE)
                    )
                    if _addr:
                        raw_address = list(_addr.find_parent().stripped_strings)[1]
                        addr = parse_address_intl(raw_address)
                    else:
                        _addr = sp1.find_all(
                            "h3", string=re.compile(r"^Roy", re.IGNORECASE)
                        )[-1]
                        if _addr:
                            raw_address = _addr.text.strip()
                            addr = parse_address_intl(raw_address)

            if not addr.postcode:
                _addr = sp1.find("a", string=re.compile(r"Reservations", re.IGNORECASE))
                if _addr:
                    raw_address = (
                        _addr.find_parent()
                        .find_parent()
                        .find_parent()
                        .find_next_sibling()
                        .text.strip()
                    )
                    addr = parse_address_intl(raw_address)

            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            city = addr.city
            if not city:
                city = raw_address.split(",")[-2].strip()
            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip().replace("’", "'"),
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
