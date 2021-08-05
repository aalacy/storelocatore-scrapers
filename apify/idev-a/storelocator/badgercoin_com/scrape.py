from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgselenium import SgFirefox
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("badgercoin")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.badgercoin.com"
base_url = "https://www.badgercoin.com/locations"


def fetch_data():
    locs = []
    with SgFirefox(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("section#location-list a")
        for x, _ in enumerate(locations):
            driver.get(_["href"])
            logger.info(_["href"])
            sp1 = bs(driver.page_source, "lxml")
            if not sp1.select_one('button[data-item-id="address"]'):
                continue
            try:
                while True:
                    try:
                        coord = (
                            driver.current_url.split("/@")[1]
                            .split("/data")[0]
                            .split(",")
                        )
                        break
                    except:
                        time.sleep(1)
                _p = sp1.select_one('button[data-tooltip="Copy phone number"]')
                phone = ""
                if _p:
                    phone = _p["aria-label"].split(":")[-1].strip()
                _hr = sp1.find("div", jsaction=re.compile(r"openhours"))
                hours = []
                if _hr:
                    for hh in _hr.find_next_sibling("div").select("table tr"):
                        hours.append(f"{hh.th.text.strip()}: {hh.td.ul.text.strip()}")
                addr = (
                    sp1.select_one('button[data-item-id="address"]')["aria-label"]
                    .split(":")[1]
                    .strip()
                    .split(",")
                )

                yield SgRecord(
                    page_url=base_url,
                    location_name=_.text.strip(),
                    street_address=" ".join(addr[:-3]),
                    city=addr[-3].strip(),
                    state=addr[-2].strip().split(" ")[0],
                    zip_postal=" ".join(addr[-2].strip().split(" ")[1:]),
                    country_code=addr[-1],
                    phone=phone,
                    latitude=coord[0],
                    longitude=coord[1],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )
            except Exception as err:
                locs = locations[x:]
                break

    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        for _ in urls:
            driver.get(_["href"])
            logger.info(_["href"])
            sp1 = bs(driver.page_source, "lxml")
            if not sp1.select_one('button[data-item-id="address"]'):
                continue
            while True:
                try:
                    coord = (
                        driver.current_url.split("/@")[1].split("/data")[0].split(",")
                    )
                    break
                except:
                    time.sleep(1)
            _p = sp1.select_one('button[data-tooltip="Copy phone number"]')
            phone = ""
            if _p:
                phone = _p["aria-label"].split(":")[-1].strip()
            _hr = sp1.find("div", jsaction=re.compile(r"openhours"))
            hours = []
            if _hr:
                for hh in _hr.find_next_sibling("div").select("table tr"):
                    hours.append(f"{hh.th.text.strip()}: {hh.td.ul.text.strip()}")
            addr = (
                sp1.select_one('button[data-item-id="address"]')["aria-label"]
                .split(":")[1]
                .strip()
                .split(",")
            )

            yield SgRecord(
                page_url=base_url,
                location_name=_.text.strip(),
                street_address=" ".join(addr[:-3]),
                city=addr[-3].strip(),
                state=addr[-2].strip().split(" ")[0],
                zip_postal=" ".join(addr[-2].strip().split(" ")[1:]),
                country_code=addr[-1],
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
