from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re
import ssl
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from tenacity import retry, stop_after_attempt, wait_fixed

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("thenomadhotel")

locator_domain = "https://thenomadhotel.com/"
base_url = "https://www.thenomadhotel.com"
url1 = "https://www.thenomadhotel.com/contact/"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


@retry(wait=wait_fixed(2), stop=stop_after_attempt(2))
def get_url(driver=None, url=None):
    if not driver:
        driver = get_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.url_contains("z/data="))
    except:
        driver = get_driver()
        raise Exception


def fetch_data():
    driver = get_driver()
    driver.get(url1)
    all_locs = bs(driver.page_source, "lxml").select("div#all section.contact-info")

    driver.get(base_url)
    soup = bs(driver.page_source, "lxml")
    links = soup.select("div.nav-bar.js-sticky nav.nav a.nav-item.nav-link")
    logger.info(f"{len(links)} found")
    for link in links:
        page_url = link["href"]
        logger.info(page_url)
        driver.get(page_url)
        sp1 = bs(driver.page_source, "lxml")
        try:
            ss = json.loads(sp1.find("script", string=re.compile(r"latitude")).string)
            hours = f"{','.join(ss['openingHoursSpecification']['dayOfWeek'])}: {ss['openingHoursSpecification']['opens']}-{ss['openingHoursSpecification']['closes']}"
            yield SgRecord(
                page_url=page_url,
                location_name=ss["name"],
                street_address=ss["address"]["streetAddress"].replace("South", ""),
                city=ss["address"]["addressLocality"],
                state=ss["address"]["addressRegion"],
                zip_postal=ss["address"]["postalCode"],
                country_code=ss["address"]["addressCountry"],
                phone=ss["telephone"],
                locator_domain=locator_domain,
                latitude=ss["geo"]["latitude"],
                longitude=ss["geo"]["longitude"],
                hours_of_operation=hours,
            )
        except:
            for loc in all_locs:
                addr = list(
                    loc.select_one("div.col-md-4")
                    .findChildren(recursive=False)[0]
                    .stripped_strings
                )
                if link.text.strip() in addr[1]:
                    map_url = loc.select_one("div.col-md-4").a["href"]
                    try:
                        get_url(driver, map_url)
                        coord = (
                            driver.current_url.split("/@")[1]
                            .split("/data")[0]
                            .split(",")
                        )
                    except:
                        import pdb

                        pdb.set_trace()
                        coord = ["", ""]
                    yield SgRecord(
                        page_url=page_url,
                        location_name=loc.h2.text.strip(),
                        street_address=addr[0],
                        city=link.text.strip(),
                        state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                        zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                        country_code="US",
                        latitude=coord[0],
                        longitude=coord[1],
                        phone=sp1.select_one("div.detail_content div a").text.strip(),
                        locator_domain=locator_domain,
                        raw_address=" ".join(addr),
                    )
                    break

    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
