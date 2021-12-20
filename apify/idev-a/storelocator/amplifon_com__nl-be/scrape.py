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

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("gaes")

locator_domain = "https://www.amplifon.com/nl-be/"
my_urls = [
    dict(
        country="Portugal",
        base_url="https://www.minisom.pt/centros-minisom",
        domain="https://www.minisom.pt",
    ),
    dict(
        country="Switzerland",
        base_url="https://www.amplifon.com/de-ch/filiale-finden",
        domain="https://www.amplifon.com",
    ),
    dict(
        country="Belgium",
        base_url="https://www.amplifon.com/nl-be/hoorcentrum",
        domain="https://www.amplifon.com",
    ),
]


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


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
    ) as driver:
        for my_url in my_urls:
            base_url = my_url["base_url"]
            country = my_url["country"]
            domain = my_url["domain"]
            locations = []
            driver.get(base_url)
            urls = (
                bs(driver.page_source, "lxml")
                .select("div.richtext-container p")[1]
                .select("a")
            )

            for url in urls:
                del driver.requests
                logger.info(domain + url["href"])
                driver.get(domain + url["href"])
                locations += [
                    loc.a["href"]
                    for loc in bs(driver.page_source, "lxml").select(
                        "div.m-store-teaser"
                    )
                ]

            driver = get_driver()
            logger.info(f"{len(locations)} locations")
            for page_url in locations:
                logger.info(f"[***] {page_url}")
                sp1 = get_bs(driver=driver, url=page_url)
                if driver.current_url == base_url:
                    continue
                _ = json.loads(sp1.find("script", type="application/ld+json").string)
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
