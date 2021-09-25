from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("monsterminigolf")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://monsterminigolf.com"
base_url = "https://monsterminigolf.com/events/"

months = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dev",
]


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.location-data")
        for _ in locations:
            page_url = _.select_one("a.more-info")["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            phone = _.select_one("div.phoney a").text.strip()
            if "coming soon" in phone.lower():
                continue
            country_code = "US"
            if "canada" in _.h2.text.lower():
                country_code = "Canada"
            if sp1.select_one("div.address p"):
                _addr = list(sp1.select_one("div.address p").stripped_strings)[:-1]
            else:
                _addr = list(_.p.stripped_strings)
            addr = parse_address_intl(" ".join(_addr))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            if sp1.select_one("div.hours"):
                if "coming soon" in sp1.select_one("div.hours").text.lower():
                    continue
                is_break = False
                for hh in sp1.select("div.hours p"):
                    if is_break:
                        break
                    for hr in hh.stripped_strings:
                        _hh = hr.lower()
                        if (
                            "see" in _hh
                            or "now open" in _hh
                            or (hours and hr.split(" ")[0][:3] in hours[0])
                        ):
                            is_break = True
                            break
                        if (
                            "we" in _hh
                            or "hours" in _hh
                            or "beginning" in _hh
                            or "/" in _hh
                            or ("open" in _hh and "open 7 days" not in _hh)
                            or _hh.split(" ")[0] in months
                        ):
                            continue
                        hours.append(hr.strip())
            else:
                _hr = sp1.find(
                    "", string=re.compile(r"^standard hours:", re.IGNORECASE)
                )
                if _hr:
                    temp = list(_hr.find_parent("p").stripped_strings)
                    for hh in _hr.find_parent("p").find_next_siblings("p"):
                        if not hh.text.strip():
                            break
                        temp += list(hh.stripped_strings)
                    for hh in temp:
                        if "hour" in hh.lower() or "of" in hh.lower():
                            continue
                        hours.append(hh)

            try:
                coord = (
                    sp1.select("a.purple-btn")[-1]["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text.strip(),
                street_address=street_address.replace(
                    "Cole Street Parking Lot 4Th Level", ""
                ),
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                phone=phone.split(":")[-1],
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
