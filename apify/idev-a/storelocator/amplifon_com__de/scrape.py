from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import time
import json
from sglogging import SgLogSetup
import ssl
from tenacity import retry, TryAgain

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification
logger = SgLogSetup().get_logger("gaes")

locator_domain = "https://www.amplifon.com/de/"
de_base_url = "https://www.amplifon.com/de/filiale-finden"
fr_base_url = "https://www.amplifon.com/fr/nous-trouver"
it_base_url = "https://www.amplifon.com/it/cerca-centro-amplifon"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def get_bs(driver=None, url=None):
    while True:
        if not driver:
            driver = get_driver()
        try:
            driver.get(url)
            break
        except:
            time.sleep(1)
            logger.info(f"retry {url}")
            driver = None

    return bs(driver.page_source, "lxml")


@retry
def get_json(driver=None, url=None):
    sp1 = get_bs(driver=driver, url=url)
    if driver.current_url in [de_base_url, it_base_url, fr_base_url]:
        return None, None
    try:
        _ = json.loads(sp1.find("script", type="application/ld+json").string)
    except:
        driver = get_driver()

    return _, sp1


def fetch_data():
    locations = []
    driver = get_driver()
    # Germany
    logger.info(" --- Germany ---")
    sp0 = get_bs(driver=driver, url=de_base_url)
    urls = sp0.select("div.richtext-container ul")[1].select("a")
    for url in urls:
        del driver.requests
        _url = url["href"]
        if not _url.startswith("http"):
            _url = "https://www.amplifon.com" + _url
        logger.info(_url)
        sp2 = get_bs(driver=driver, url=_url)
        locations += [
            loc["href"]
            for loc in sp2.select("div.richtext-container.am-accordion-content a")
        ]

    # France
    logger.info(" --- France ---")
    sp0 = get_bs(driver=driver, url=fr_base_url)
    urls = sp0.select("div.richtext-container table tbody tr a")
    for url in urls:
        del driver.requests
        _url = url["href"]
        if not _url.startswith("http"):
            _url = "https://www.amplifon.com" + _url
        logger.info(_url)
        sp2 = get_bs(driver=driver, url=_url)
        locations += [
            loc.a["href"] for loc in sp2.select("article.m-store-teaser-item")
        ]

    # Italy
    logger.info(" --- Italy ---")
    sp0 = get_bs(driver=driver, url=it_base_url)
    urls = sp0.select("div.richtext-container")[0].select("a")
    for url in urls:
        del driver.requests
        _url = url["href"]
        if not _url.startswith("http"):
            _url = "https://www.amplifon.com" + _url
        logger.info(_url)
        sp2 = get_bs(driver=driver, url=_url)
        locations += [
            loc.a["href"] for loc in sp2.select("div.richtext-container ul li")
        ]

    driver = get_driver()
    logger.info(f"{len(locations)} locations")
    for page_url in locations:
        logger.info(f"[***] {page_url}")
        _, sp1 = get_json(driver, page_url)
        if not _ or not sp1:
            continue
        phone = ""
        if sp1.select_one("span.phone-list"):
            phone = sp1.select_one("span.phone-list").text.strip()
        hours = []
        for hh in _["openingHoursSpecification"]:
            day = hh["dayOfWeek"]
            hours.append(f"{day}: {hh['opens']} - {hh['closes']}")
        addr = _["address"]
        yield SgRecord(
            page_url=page_url,
            location_name=_["name"],
            street_address=addr["streetAddress"],
            city=addr["addressLocality"],
            state=addr["addressRegion"],
            zip_postal=addr["postalCode"],
            latitude=_["geo"]["latitude"],
            longitude=_["geo"]["longitude"],
            country_code=addr["addressCountry"],
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
