from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("krokodil")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.krokodil.be/"
base_url = "https://www.krokodil.be/"


def _p(val):
    if (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def _d(page_url, country, location_name, raw_address, phone, hours):
    addr = parse_address_intl(raw_address + ", " + country)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code=country,
        phone=phone.replace(":", "").strip(),
        locator_domain=locator_domain,
        hours_of_operation=hours,
        raw_address=raw_address,
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("select#sel-shops option")[1:]
        for _ in locations:
            page_url = _["value"]
            if not page_url.startswith("http"):
                page_url = "https://" + page_url
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            location_name = _.text.strip()
            if "brugge" in page_url:
                hours = (
                    sp1.find("strong", string=re.compile(r"^Openingsuren:"))
                    .find_parent("p")
                    .find_next_sibling()
                    .text.strip()
                )
                block = list(sp1.select("div.middle p")[-3].stripped_strings)
                raw_address = block[0].replace("/", "")
                phone = block[-1][1:].strip()
                yield _d(page_url, "Belgium", location_name, raw_address, phone, hours)

            elif "haarlem" in page_url:
                raw_address = (
                    sp1.find("p", string=re.compile(r"^Openingstijden:"))
                    .find_previous_sibling("p")
                    .text.strip()
                )
                hours = []
                phone = ""
                for bb in sp1.find(
                    "p", string=re.compile(r"^Openingstijden:")
                ).find_next_siblings("p"):
                    _bb = bb.text.replace("\xa0", "").strip()
                    if "telefoonnr" in _bb:
                        phone = _bb.replace("telefoonnr", "").replace(".", "").strip()
                        break
                    hours.append(_bb)
                yield _d(
                    page_url,
                    "The Netherlands",
                    location_name,
                    raw_address,
                    phone,
                    "; ".join(hours),
                )

            elif "kasterlee" in page_url:
                hours = []
                for hh in (
                    sp1.find("", string=re.compile(r"Openingsuren"))
                    .find_parent("p")
                    .find_next_siblings("p")
                ):
                    _hr = hh.text.strip()
                    if not _hr:
                        break
                    hours.append(_hr)
                addr = []
                phone = ""
                for aa in (
                    sp1.find_all("", string=re.compile(r"Krokodil Kasterlee"))[-1]
                    .find_parent("p")
                    .find_next_siblings("p")
                ):
                    _hr = aa.text.strip()
                    if "Tel" in _hr:
                        phone = _hr.replace("Tel", "").replace(".", "").strip()
                        break
                    addr.append(_hr)

                yield _d(
                    page_url,
                    "Belgium",
                    location_name,
                    ", ".join(addr),
                    phone,
                    "; ".join(hours),
                )

            elif "schilde" in page_url:
                hours = []
                for hh in (
                    sp1.find("", string=re.compile(r"Openingsuren"))
                    .find_parent("p")
                    .find_next_siblings("p")
                ):
                    _hr = hh.text.strip()
                    if not _hr:
                        break
                    hours.append(_hr)

                addr = []
                phone = ""
                for aa in (
                    sp1.find("", string=re.compile(r"Adres"))
                    .find_parent("p")
                    .find_next_siblings("p")
                ):
                    _hr = aa.text.strip()
                    if "mail" in _hr:
                        continue
                    if "tel" in _hr:
                        phone = _hr.replace("tel", "").replace(".", "").strip()
                        break
                    addr.append(_hr)
                temp = [" ".join(hours[:2])]
                temp += hours[2:]
                yield _d(
                    page_url,
                    "Belgium",
                    location_name,
                    ", ".join(addr),
                    phone,
                    "; ".join(temp),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
