from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data(sgw: SgWriter):
    class_name = "site-content"
    locator_domain = "https://www.auchan-retail.com/en/"
    url = "https://www.auchan-retail.com/en/location/"
    driver = get_driver(url, class_name)
    soup = bs(driver.page_source, "html.parser")
    articles = soup.find_all("article")

    for article in articles:
        loc_name = article.find("a").text
        loc_url = article.find("a")["href"]
        address = article.find("h6")
        if address is None:
            address = SgRecord.MISSING
        else:
            address = address.text

        try:
            class_name = "site"
            driver = get_driver(loc_url, class_name)
            soup = bs(driver.page_source, "html.parser")
            info = soup.find("script", {"id": "single_location_script-js-extra"})
            info = str(info).split('latitude":"')[-1]
            [lat, info] = info.split('","longitude":"')
            [long, info] = info.split('","country":"')
            country = info.split('"')[0]
        except:
            lat = SgRecord.MISSING
            long = SgRecord.MISSING
            country = SgRecord.MISSING

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=loc_url,
                location_name=loc_name,
                raw_address=address,
                country_code=country,
                latitude=lat,
                longitude=long,
            )
        )


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)


scrape()
