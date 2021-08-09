from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgselenium import SgFirefox
import time
import json
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("muji")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _h(val):
    _val = (
        val.replace("–", "-")
        .replace("\u3000", " ")
        .replace("Click & Meet:", "")
        .strip()
    )
    _hr = _val.split(",")
    hours = []
    for hh in _hr:
        if "holiday" in hh.lower():
            continue
        hours.append(hh)

    return "; ".join(hours)


def fetch_data():
    locator_domain = "https://www.muji.com/"
    base_url = "https://www.muji.com/storelocator/"
    json_url = "https://www.muji.com/storelocator/?_ACTION="
    with SgFirefox() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div.countriesList ul li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            country_code = page_url.split("c=")[1].split("&")[0]
            logger.info(page_url)
            x = 0
            while True:
                try:
                    driver.get(page_url)
                    break
                except Exception:
                    x = x + 1
                    if x == 10:
                        raise Exception
            exist = False
            while not exist:
                time.sleep(1)
                for rr in driver.requests[::-1]:
                    if rr.url.startswith(json_url) and rr.response:
                        exist = True
                        locations = json.loads(rr.response.body)
                        for _ in locations:
                            addr = parse_address_intl(_["shopaddress"])
                            street_address = addr.street_address_1
                            if addr.street_address_2:
                                street_address += " " + addr.street_address_2
                            yield SgRecord(
                                page_url=page_url,
                                location_name=_["shopname"],
                                street_address=street_address,
                                city=addr.city,
                                state=addr.state,
                                zip_postal=addr.postcode,
                                country_code=country_code,
                                phone=_["tel"].replace("\u3000", " ").strip(),
                                locator_domain=locator_domain,
                                latitude=_["latitude"],
                                longitude=_["longitude"],
                                hours_of_operation=_h(_["opentime"]),
                            )

                        break


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
