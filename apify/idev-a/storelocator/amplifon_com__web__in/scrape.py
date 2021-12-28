from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from tenacity import retry, stop_after_attempt, wait_fixed
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("gaes")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.amplifon.com"
ss_urls = {
    "IN": "https://www.amplifon.com/web/in/store-locator",
}

hu_url = "https://www.amplifon.com/web/hu/hallaskozpont-kereso"
pl_url = "https://www.amplifon.com/pl/nasze-gabinety"


def fetch_data():
    with SgRequests() as session:
        for country, base_url in ss_urls.items():
            locations = json.loads(
                session.get(base_url, headers=_headers)
                .text.split("var shopLocator=")[1]
                .split("var amplifonShopURL=")[0]
                .strip()[:-1]
            )
            for _ in locations:
                page_url = f"{base_url}/-/store/amplifon-point/{_['shopNumber']}/{_['shopNameForUrl']}/{_['cityForUrl']}/{_['addressForUrl']}"
                if country == "country":
                    page_url = base_url
                state = _["province"]
                if state == "0":
                    state = ""
                phone = _["phoneInfo1"]
                if not phone:
                    phone = _.get("phoneNumber1")
                if not phone:
                    phone = _.get("phoneNumber2")
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["shopName"],
                    street_address=_["address"],
                    city=_["city"],
                    state=state,
                    zip_postal=_["cap"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation=_["openingTime"],
                )


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


@retry(wait=wait_fixed(2), stop=stop_after_attempt(7))
def get_bs(driver=None, url=None):
    if not driver:
        driver = get_driver()
    try:
        driver.get(url)
    except:
        driver = get_driver()
        raise Exception

    return bs(driver.page_source, "lxml")


def fetch_chrome():
    driver = get_driver()
    urls = {}
    driver.get(hu_url)
    urls["hu"] = (
        bs(driver.page_source, "lxml").select("div.richtext-container p")[1].select("a")
    )
    driver.get(pl_url)
    urls["pl"] = (
        bs(driver.page_source, "lxml").select("div.richtext-container p")[0].select("a")
    )
    for country, url1 in urls.items():
        for url in url1:
            del driver.requests
            _url = "https://www.amplifon.com" + url["href"]
            logger.info(_url)
            sp0 = get_bs(driver=driver, url=_url)
            for loc in sp0.select("div.m-store-teaser-list div.m-store-teaser"):
                if not loc.a:
                    continue
                page_url = loc.a["href"]
                if not page_url.startswith("http"):
                    page_url = locator_domain + page_url

                logger.info(f"[***] {page_url}")
                sp1 = get_bs(driver=driver, url=page_url)
                if driver.current_url == hu_url or driver.current_url == pl_url:
                    continue
                _ = json.loads(sp1.find("script", type="application/ld+json").string)
                phone = ""
                if sp1.select_one("span.phone-list"):
                    try:
                        phone = list(
                            sp1.select_one("span.phone-list").stripped_strings
                        )[0]
                    except:
                        pass
                hours = []
                for hh in _["openingHoursSpecification"]:
                    day = hh["dayOfWeek"]
                    hours.append(f"{day}: {hh['opens']} - {hh['closes']}")
                addr = _["address"]
                state = addr.get("addressRegion")
                if (
                    state.replace("(", "")
                    .replace(")", "")
                    .replace(" ", "")
                    .strip()
                    .isdigit()
                ):
                    state = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=addr["streetAddress"],
                    city=addr["addressLocality"],
                    state=state,
                    zip_postal=addr.get("postalCode"),
                    latitude=_["geo"]["latitude"],
                    longitude=_["geo"]["longitude"],
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )

    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

        results = fetch_chrome()
        for rec in results:
            writer.write_row(rec)
