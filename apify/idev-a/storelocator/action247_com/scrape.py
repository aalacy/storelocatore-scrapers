from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = "https://www.action247.com"
base_url = "https://www.action247.com/cashlocations/"
json_url = "/api/v1/maps/map_2e743d53/layers/pg_67899b52"


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


def _d(res, url):
    sp1 = bs(res.text, "lxml")
    ii = sp1.find("span", string=re.compile(r"^Info"))
    block = []
    for bb in ii.find_parent().find_next_siblings():
        block += list(bb.stripped_strings)

    phone = ""
    if _p(block[-1]):
        phone = block[-1]
        del block[-1]

    if block[-1] == "US":
        del block[-1]
    raw_address = ", ".join(block[1:])
    addr = parse_address_intl(raw_address + ", United States")
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    hours = []
    if len(sp1.select("table.store-table")) > 1:
        days = list(sp1.select("table.store-table")[0].select("td")[0].stripped_strings)
        times = list(
            sp1.select("table.store-table")[0].select("td")[1].stripped_strings
        )
        for x in range(len(days)):
            hours.append(f"{days[x]}: {times[x]}")
    latitude = res.text.split("latitude")[1].split(";")[0].replace("=", "").strip()
    longitude = res.text.split("longitude")[1].split(";")[0].replace("=", "").strip()
    return SgRecord(
        page_url=url,
        location_name=list(sp1.select_one("main#main h3").stripped_strings)[0],
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        latitude=latitude,
        longitude=longitude,
        country_code="US",
        phone=_p(phone),
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
        raw_address=raw_address,
    )


def fetch_data(writer):
    with SgRequests(proxy_country="us") as http:
        locations = bs(http.get(base_url, headers=_headers).text, "lxml").select(
            "div#primary table td"
        )
        for link in locations:
            url = link.a["href"]
            logger.info(url)
            res = http.get(url, headers=_headers)
            if res.status_code != 200:
                continue
            sp1 = bs(res, "lxml")
            locs = [loc.a["href"] for loc in sp1.select("main#main table td") if loc.a]
            if locs:
                for page_url in locs:
                    logger.info(page_url)
                    res = http.get(page_url, headers=_headers)
                    if res.status_code != 200:
                        continue
                    writer.write_row(_d(res, page_url))
            else:
                writer.write_row(_d(res, url))


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data(writer)
