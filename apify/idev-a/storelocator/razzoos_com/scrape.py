from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
import re
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

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


def _hour(_pp):
    hours = []
    temp = []
    if _pp.name == "strong":
        _pp = _pp.find_parent()

    for hh in _pp.find_next_siblings("h3"):
        hr = hh.text.strip()
        if not hr or "seating" in hr:
            break
        temp.append(hh.text.replace("*", "").strip())
    for x in range(0, len(temp), 2):
        hours.append(f"{temp[x]} {temp[x+1]}")

    return hours


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
            raw_address = " ".join(_addr)
            addr = parse_address_intl(raw_address)
            street_address = " ".join(_addr[:-1])
            if not street_address:
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
            phone = ""
            hours = []
            _hr = sp1.find("", string=re.compile(r"^Phone"))
            if _hr:
                phone = (
                    list(_hr.find_parent("h3").stripped_strings)[-1]
                    .split(":")[-1]
                    .replace("(", "")
                    .replace(")", "")
                )
                hours = _hour(_hr.find_parent())
            else:
                _hr = sp1.select_one(
                    "main div.sqs-row div.sqs-row div.sqs-col-4 div.html-block div.sqs-block-content p"
                )
                if _hr:
                    phone = _hr.text.strip()
                    hours = _hour(_hr)
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
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
