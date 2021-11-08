from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import time
import dirtyjson as json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("baskinrobbins")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "m.baskinrobbins.co.kr",
    "Origin": "http://m.baskinrobbins.co.kr",
    "Referer": "http://m.baskinrobbins.co.kr/store/map.php",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.baskinrobbins.co.kr"
base_url = "http://m.baskinrobbins.co.kr/store/map.php"
gun_url = "/store/addr_gugun_ajax"
list_url = "/store/list_ajax.php"
detail_url = "http://m.baskinrobbins.co.kr/store/store_info_ajax.php?S={}"


def _d(_, http):
    logger.info(_["storeCode"])
    res = http.get(detail_url.format(_["storeCode"]), headers=_headers)
    try:
        loc = json.loads(res.text.split("\n")[-1])
        return SgRecord(
            page_url=base_url,
            store_number=_["storeCode"],
            location_name=_["name"],
            street_address=_["address3"],
            city=_["address2"],
            state=_["address1"],
            country_code="Korea",
            phone=_["tel"],
            latitude=_["pointY"],
            longitude=_["pointX"],
            locator_domain=locator_domain,
            hours_of_operation=loc.get("time", "").replace("&#58;", "-"),
            raw_address=_["address"],
        )
    except:
        pass


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as http:
            # get initial page
            locations = http.get(
                "http://www.baskinrobbins.co.kr/store/list_ajax.php?ScS=&ScG=&ScWord="
            ).json()["list"]
            for _ in locations:
                yield _d(_, http)

            driver.get(base_url)
            states = driver.find_elements_by_css_selector("select.location_1 option")
            logger.info(f"{len(states)} states")
            for state in states:
                state_val = state.get_attribute("value")
                if not state_val:
                    continue
                del driver.requests
                state.click()
                driver.wait_for_request(gun_url)
                cities = driver.find_elements_by_css_selector(
                    "select.location_2 option"
                )
                logger.info(f"[{state_val}] {len(cities)} cities")
                for gun in cities:
                    gun_val = gun.get_attribute("value")
                    if not gun_val:
                        continue
                    del driver.requests
                    gun.click()
                    time.sleep(1)
                    driver.find_element_by_css_selector(
                        'div.search button[type="submit"]'
                    ).click()
                    lr = driver.wait_for_request(list_url)
                    try:
                        res = json.loads(lr.response.body)
                    except:
                        try:
                            res = http.get(lr.url).json()
                        except:
                            continue
                    if res.get("cnt") > 0:
                        locations = res["list"]
                    else:
                        continue
                    logger.info(f"[{gun_val}] {len(locations)} locations")
                    for _ in locations:
                        yield _d(_, http)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
