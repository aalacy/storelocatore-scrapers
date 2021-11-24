import re
import json
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
    class_name = "container-fluid"
    url = "http://www.miranchitorestaurants.com/"
    driver = get_driver(url, class_name)
    soup = bs(driver.page_source, "html.parser")
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    for script in scripts:
        loc_data = json.loads(re.findall(r"{.*}", str(script))[0])
        hoo = ", ".join(loc_data["openingHours"]).strip()
        loc = loc_data["address"]["addressLocality"]
        loc_url = url + loc.lower().replace(" ", "-")
        street_address = loc_data["address"]["streetAddress"]
        regex = f'(?<={street_address}).*?(?="menuLandingPageUrl")'
        coords = re.findall(regex, str(soup))
        lat, long = re.findall(r'"lat":(-?[\d\.]+),"lng":(-?[\d\.]+)', str(coords))[0]

        sgw.write_row(
            SgRecord(
                locator_domain=url,
                page_url=loc_url,
                location_name=loc,
                street_address=street_address,
                city=loc,
                state=loc_data["address"]["addressRegion"],
                zip_postal=loc_data["address"]["postalCode"],
                country_code=SgRecord.MISSING,
                store_number=SgRecord.MISSING,
                phone=loc_data["address"]["telephone"],
                location_type=loc_data["@type"],
                latitude=lat,
                longitude=long,
                hours_of_operation=hoo,
            )
        )


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)


scrape()
