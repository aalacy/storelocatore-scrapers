from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
import ssl
import time

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("royalbluegrocery")

locator_domain = "https://www.royalbluegrocery.com/"
base_url = "https://www.royalbluegrocery.com/locations"
json_url = "https://siteassets.parastorage.com/pages/pages/thunderbolt"


def _pp(locs, street):
    for loc in locs:
        if (
            " ".join(street.lower().split()[:2])
            in loc.select_one("div.info-element-description span").text.lower()
        ):
            return loc.select("div.info-element-description span")[-1].text.strip()

    return ""


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        driver.get(base_url)
        sp = bs(driver.page_source, "lxml")
        _loc = sp.find(
            "a", href=re.compile(r"https://www.royalbluegrocery.com/locations")
        )
        links = _loc.find_parent().find_parent().find_next_sibling("ul").select("li a")
        locs = sp.select("div.gallery-item-container div.gallery-item-common-info")
        for _ in links:
            page_url = _["href"]
            logger.info(page_url)
            del driver.requests
            time.sleep(1)

            driver.get(page_url)
            driver.wait_for_request(json_url)
            ss = {}
            info = {}
            for rr in driver.iter_requests():
                try:
                    if json_url in rr.url:
                        ss = json.loads(rr.response.body)["props"]["render"][
                            "compProps"
                        ]
                        for key, val in ss.items():
                            if val.get("mapData"):
                                info = val["mapData"]["locations"][0]
                                break
                        if info:
                            break
                except:
                    logger.warning("^^^ next url")
            addr = info["address"].split(",")
            sp1 = bs(driver.page_source, "lxml")
            street_address = " ".join(addr[:-3])
            data = []
            h6_font = sp1.select("h6.font_6")
            for h6 in h6_font:
                if "every" in h6.text.lower() or "open" in h6.text.lower():
                    data = list(h6.stripped_strings)
                    if len(data) == 1:
                        hours = data[0].split("•")[-1]
                    else:
                        hours = data[-1]

                    break

            phone = _pp(locs, street_address)
            if not phone:
                import pdb

                pdb.set_trace()
            yield SgRecord(
                page_url=page_url,
                location_name=_.text.strip(),
                street_address=street_address,
                city=addr[-3].strip(),
                state=addr[-2].strip().split()[0].strip(),
                zip_postal=addr[-2].strip().split()[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours.replace("\xa0", "").strip(),
                raw_address=info["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
