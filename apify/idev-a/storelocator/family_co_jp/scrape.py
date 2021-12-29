from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager
import ssl
from sglogging import SgLogSetup
from tenacity import retry, wait_fixed, stop_after_attempt

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("family")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://family.co.jp/"
base_url = "https://as.chizumaru.com/famimatg/top?account=famimatg&accmd=0"
pref_url = "https://as.chizumaru.com/famimatg/articleList?account=famimatg&accmd=0&searchType=True&adr={}&c2=1&pg=1&pageSize=10000&pageLimit=10000&template=Ctrl%2fDispListArticle_g12"
prefecture_url = "https://en.wikipedia.org/wiki/Prefectures_of_Japan"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def get_data(driver, url):
    driver.get(url)
    locations = []
    try:
        locations = bs(driver.page_source, "lxml").select(
            "div#DispListArticle div.cz_articlelist_box dl.cz_accordion"
        )
    except:
        driver.close()
        driver = get_driver()

    return locations


def fetch_data():
    driver = get_driver()
    with SgRequests(verify_ssl=False) as session:
        prefectures = []
        for pref in bs(
            session.get(prefecture_url, headers=_headers).text, "lxml"
        ).select("table.wikitable.sortable tbody tr"):
            if pref.th:
                continue
            prefectures.append(pref.select("td")[1].text.strip())

        driver.get(base_url)
        prefs = bs(driver.page_source, "lxml").select("select.cz_select01 option")
        for pref in prefs:
            if not pref.get("value"):
                continue
            locations = get_data(driver, pref_url.format(pref["value"]))
            logger.info(f"{pref['value']} {len(locations)}")
            for _ in locations:
                tr = _.select("table tbody tr")
                page_url = "https://as.chizumaru.com" + tr[0].a["href"]
                raw_address = tr[1].td.text.strip()
                street_address = city = state = ""
                for pref in prefectures:
                    if pref in raw_address:
                        state = pref
                        break
                street_address = _city = raw_address
                if state:
                    street_address = _city = raw_address.replace(state, "")
                if "市" in _city:
                    _city = _city.split("市")
                    if len(_city) > 1:
                        city = _city[0] + "市"
                if city:
                    street_address = street_address.replace(city, "")
                if state == "東京都":
                    city = state
                    state = ""

                yield SgRecord(
                    page_url=page_url,
                    location_name=tr[0].td.text.strip(),
                    street_address=street_address,
                    city=city,
                    state=state,
                    country_code="JP",
                    phone=tr[2].td.text.strip(),
                    locator_domain=locator_domain,
                    hours_of_operation=tr[3].td.text.split("祝は")[0].strip(),
                    raw_address=raw_address,
                )

    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
