from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import time

logger = SgLogSetup().get_logger("wellsfargo")

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "www.wellsfargo.com",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.wellsfargo.com/"
    base_url = "https://www.wellsfargo.com/locator/"
    payload_url = "https://www.wellsfargo.com/locator/as/getpayload"
    with SgChrome(executable_path=r"/mnt/g/work/mia/chromedriver.exe") as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        states = soup.select("map#theImageMap area")
        logger.info(f"[states] {len(states)} states")
        total = 0
        for state in states:
            _state = state["href"].replace("#", "")
            state_url = f"https://www.wellsfargo.com/locator/as/getCities/{_state}"
            with SgRequests() as session:
                cities = json.loads(
                    session.get(state_url, headers=_headers)
                    .text.split("/*WellsFargoProprietary%")[1]
                    .split("%WellsFargoProprietary*/")[0]
                    .strip()
                )["allCities"]
                logger.info(f"[{_state}] {len(cities)} cities")
                for city in cities:
                    city_url = f"https://www.wellsfargo.com/locator/search/?searchTxt={city}%2C+{_state}&mlflg=N&sgindex=99&chflg=Y&_bo=on&_wl=on&_os=on&bdu=1&_bdu=on&adu=1&_adu=on&ah=1&_ah=on&_sdb=on&_aa=on&_nt=on&_fe=on"
                    driver.get(city_url)
                    exist = False
                    locations = []
                    while not exist:
                        time.sleep(1)
                        logger.info(f"[{city}] waiting ....")
                        for rr in driver.requests[::-1]:
                            if rr.url == payload_url and rr.response:
                                exist = True
                                locations = json.loads(rr.response.body)[
                                    "searchResults"
                                ]
                                break

                    total += len(locations)
                    logger.info(
                        f"[total {total}] [{_state}] [{city}] {len(locations)} locations"
                    )
                    for _ in locations:
                        page_url = f"https://www.wellsfargo.com/locator/bank/?slindex={_['index']}"
                        yield SgRecord(
                            page_url=page_url,
                            store_number=_["index"],
                            location_name=_["branchName"],
                            street_address=_["locationLine1Address"],
                            city=_["city"],
                            state=_["state"],
                            zip_postal=_["postalcode"],
                            country_code="US",
                            latitude=_["latitude"],
                            location_type=_["locationType"],
                            longitude=_["longitude"],
                            phone=_["phone"],
                            locator_domain=locator_domain,
                            hours_of_operation="; ".join(_.get("arrDriveUpHours", [])),
                        )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
