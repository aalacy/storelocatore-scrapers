import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

locator_domain = "https://www.eblens.com"
base_url = "https://www.eblens.com/functions/storelocator.cfc?method=generateStoreLocatorResultsAJAX&random=69"


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


def fetch_records(session, search):
    for zip_code in search:
        payload = {"locationSearch": zip_code, "maxrows": 20}
        res = session.post(base_url, data=payload)
        if res.status_code != 200:
            continue
        soup = bs(json.loads(res.text)["STOREDISP"], "lxml")
        locations = soup.select("div.mapAddress")
        logger.info(f"[{zip_code}] {len(locations)}")
        for store in locations:
            page_url = store.select_one("span.store_detail a")["href"]
            location_name = store.select_one("a.store_name").text.strip()
            if "Closed" in location_name:
                location_name += " Closed"
            addr = list(store.select_one("span.store_addr").stripped_strings)
            phone = ""
            if _p(addr[-1]):
                phone = addr[-1]
                del addr[-1]
            geo = (
                store.select_one("span.store_directions a")["href"]
                .split("sll=")[1]
                .split("&")[0]
                .split(",")
            )
            detail = bs(session.get(page_url).text, "lxml")
            hours_of_operation = ""
            if detail.select_one("ul.storeHours"):
                hours_of_operation = detail.select_one("ul.storeHours").text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=geo[0],
                longitude=geo[1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgRequests() as http:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], granularity=Grain_8()
        )
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
            )
        ) as writer:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
