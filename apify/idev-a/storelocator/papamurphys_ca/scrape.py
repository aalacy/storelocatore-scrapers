from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("papamurphys")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://papamurphys.ca/"
base_url = "https://papa-murphys-order-online-locations.securebrygid.com/zgrid/themes/13097/portal/index.jsp"


def _p(val):
    if (
        val
        and val.replace("(", "")
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


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.restaurant")
        logger.info(f"{len(links)} found")
        for link in links:
            _addr = list(link.p.stripped_strings)
            raw_address = " ".join(_addr[:2])
            addr = parse_address_intl(raw_address + ", Canada")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if _p(_addr[2]):
                phone = _addr[2]
            hours = []
            if len(link.select("p")) > 1:
                for hh in link.select("p")[1].stripped_strings:
                    if "delivery" in hh.lower():
                        break
                    hours.append(hh)

            page_url = base_url
            if link.select_one("a.portalbtn"):
                page_url = link.select_one("a.portalbtn")["href"]

            yield SgRecord(
                page_url=page_url,
                location_name=link.h6.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
