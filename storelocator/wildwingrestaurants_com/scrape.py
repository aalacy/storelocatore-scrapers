from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl


logger = SgLogSetup().get_logger("wildwingrestaurants")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.wildwingrestaurants.com"
base_url = "https://www.wildwingrestaurants.com/locations/"


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
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split('"locations":')[1]
            .split("jQuery(document")[0]
            .strip()[:-1]
        )
        for _ in locations:
            _addr = list(bs(_["address"], "lxml").stripped_strings)
            if _["title"] in _addr[0]:
                del _addr[0]
            phone = _addr[-1].split(":")[-1].replace("Phone", "")
            if not _p(phone):
                phone = ""
            else:
                del _addr[-1]
            if "Phone" in _addr[-1]:
                del _addr[-1]
            if "Open today" in _addr[-1]:
                del _addr[-1]
            addr = parse_address_intl(" ".join(_addr))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            state = addr.state
            zip_postal = addr.postcode
            if not state or not zip_postal or len(zip_postal) == 3:
                s_z = (
                    _addr[-1].replace(addr.city, "").replace(",", "").strip().split(" ")
                )
                state = s_z[0].strip()
                zip_postal = " ".join(s_z[1:])

            page_url = _["view_location"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select(
                    'div[data-rel="scroll-location-detail"] div.hours-row'
                )
            ]
            hours_of_operation = "; ".join(hours).replace("–", "-")
            if "Hours vary" in hours_of_operation:
                hours_of_operation = ""
            yield SgRecord(
                page_url=page_url,
                location_name=_["title"]
                .replace("’", "'")
                .replace("&#8211;", "-")
                .replace("–", "-")
                .replace("&#038;", "&")
                .replace("NOW OPEN", ""),
                street_address=street_address,
                city=addr.city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
