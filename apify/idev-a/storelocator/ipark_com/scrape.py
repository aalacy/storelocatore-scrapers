from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from datetime import datetime
import re
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ipark")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ipark.com"
base_url = "https://ipark.com/wp-admin/admin-ajax.php?action=set_all_markers&filters%5B%5D=locations&nonce=8e8a914d40"


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


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            data = {
                "action": "get_garage_details",
                "garage_id": str(_[3]),
                "enter": now,
                "exit": now,
                "vehicle": "regular",
                "nonce": "8e8a914d40",
            }
            logger.info(_[3])
            loc = bs(
                session.post(
                    "https://ipark.com/wp-admin/admin-ajax.php",
                    headers=_headers,
                    data=data,
                ).text,
                "lxml",
            )
            raw_address = loc.select_one("div.garage-address").text.strip()
            if "United States" not in raw_address:
                raw_address += ", United States"
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if not city and "Brooklyn" in raw_address:
                city = "Brooklyn"
            if "Long Island City" in raw_address:
                city = "Long Island City"
            if city and city == "36Th":
                city = ""
                street_address = raw_address.split(",")[0]
            phone = ""
            if loc.find("strong", string=re.compile(r"Phone Number:")):
                for pp in list(
                    loc.find("strong", string=re.compile(r"Phone Number:"))
                    .find_parent()
                    .stripped_strings
                ):
                    if _p(pp):
                        phone = pp
                        break
            hours = []
            _hr = loc.find("strong", string=re.compile(r"Operation Hours:"))
            if _hr:
                hours = list(_hr.find_parent().stripped_strings)[1:]
            yield SgRecord(
                page_url=loc.select_one("div.garage-link a")["href"],
                store_number=_[3],
                location_name=_[4].replace("&#8211;", "-"),
                street_address=street_address.replace("&#8211;", "-"),
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_[1],
                longitude=_[2],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
