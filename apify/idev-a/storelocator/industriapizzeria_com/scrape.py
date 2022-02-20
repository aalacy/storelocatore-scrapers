from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("industriapizzeria")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.replace("–", "-").strip()


def fetch_data():
    locator_domain = "https://industriapizzeria.com"
    base_url = "https://industriapizzeria.com/our-restaurants/ottawa/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.restaurant-list ul li a")
        for _ in locations:
            page_url = locator_domain + _["href"]
            logger.info(page_url)
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            coming = [
                hh.text
                for hh in soup1.select("div.entry-content.our-restaurants p")[1:]
            ]
            if "COMING SOON" in coming:
                continue
            hours = []
            _hr = soup1.find("strong", string=re.compile(r"^OPENING HOURS"))
            if _hr:
                temp = list(_hr.find_parent().find_next_sibling().stripped_strings)
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]} {temp[x+1]}")
            if hours and not re.search(r"tel:", hours[-1], re.IGNORECASE):
                del hours[-1]
            raw_address = []
            for aa in list(
                soup1.select_one("div.entry-content.our-restaurants p").stripped_strings
            ):
                if "Address" in aa:
                    continue
                if (
                    "contact" in aa.lower()
                    or "open" in aa.lower()
                    or "Centre" in aa
                    or "Centrum" in aa
                ):
                    break
                raw_address.append(", ".join(aa.split("|")))
            addr = parse_address_intl(" ".join(raw_address) + ", Canada")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if "St.Catharines" in street_address:
                city = "St.Catharines"
            phone = ""
            if soup1.find("a", href=re.compile(r"tel:")):
                phone = soup1.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_.text,
                street_address=street_address.replace("St.Catharines", "").strip(),
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(raw_address),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
