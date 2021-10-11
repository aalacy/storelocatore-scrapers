from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import re
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("genejuarez")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://www.genejuarez.com/"
    base_url = "https://www.genejuarez.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#locations div.column a")
        logger.info(f"{len(links)} found")
        for link in links:
            if "Closed" in link.text.strip():
                continue
            page_url = link["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            raw_address = longitude = latitude = ""
            if len(res.split("var gmpAllMapsInfo =")) > 1:
                script = json.loads(
                    res.split("var gmpAllMapsInfo =")[1]
                    .split("/* ]]> */")[0]
                    .strip()[:-1]
                )[0]
                raw_address = " ".join(
                    bs(script["markers"][0]["description"], "lxml").stripped_strings
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
                latitude = script["markers"][0]["coord_x"]
                longitude = script["markers"][0]["coord_y"]
            else:
                addr = list(sp1.select_one("div#visit p").stripped_strings)
                raw_address = " ".join(addr)
                street_address = " ".join(addr[:-1])
                city = addr[-1].split(",")[0].strip()
                state = addr[-1].split(",")[1].strip().split(" ")[0].strip()
                zip_postal = addr[-1].split(",")[1].strip().split(" ")[-1].strip()
            hours = []
            mon = sp1.find("strong", string=re.compile(r"Monday"))
            times = []
            _hr = []
            _br = list(mon.find_parent().stripped_strings)
            for x, hh in enumerate(_br):
                if x == len(_br) - 1:
                    times.append(hh)
                    _hr.append("".join(times))
                if hh in days:
                    if times:
                        _hr.append("".join(times))
                    _hr.append(hh)
                    times = []
                else:
                    times.append(hh)
            for x in range(0, len(_hr), 2):
                hours.append(f"{_hr[x]}: {_hr[x+1]}")
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                phone=sp1.find("a", href=re.compile(r"tel:"))
                .text.replace("Call or text", "")
                .strip(),
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
