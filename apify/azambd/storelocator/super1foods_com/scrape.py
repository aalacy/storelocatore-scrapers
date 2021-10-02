from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sglogging import sglog

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

locator_domain = "super1foods.com"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


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

            WebDriverWait(driver, 30).until(
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


def fetch_data():

    x = 0
    while True:
        x = x + 1
        class_name = "store-preview__info"
        url = "https://www.super1foods.com/stores/?coordinates=36.01301919805139,-124.22992541516308&zoom=1"
        if x == 1:
            driver = get_driver(url, class_name)
        else:
            driver = get_driver(url, class_name, driver=driver)
        soup = bs(driver.page_source, "html.parser")
        grids = soup.find("div", class_="store-list__scroll-container").find_all("li")
        log.info(f"Total Locations: {len(grids)}")
        if len(grids) == 0:
            continue
        else:
            break

    for grid in grids:
        name = grid.find(
            "span", attrs={"ng-class": "{ 'sr-only': $ctrl.store._match }"}
        ).text.strip()
        number = grid.find(
            "span",
            attrs={"ng-if": "$ctrl.showStoreNumber && $ctrl.store.storeNumber"},
        ).text.strip()
        page_url = (
            "https://www.super1foods.com/stores/"
            + name.split("\n")[0].replace(" ", "-").replace(".", "").lower()
            + "-"
            + number.split("\n")[0].split("#")[-1]
            + "/"
            + grid["id"].split("-")[-1]
        )
        try:
            driver.get(page_url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "store-details-store-hours__content")
                )
            )
        except Exception:
            driver = get_driver(
                page_url, "store-details-store-hours__content", driver=driver
            )

        location_soup = bs(driver.page_source, "html.parser")

        location_name = location_soup.find("meta", attrs={"property": "og:title"})[
            "content"
        ]
        address = location_soup.find("meta", attrs={"property": "og:street-address"})[
            "content"
        ]
        city = location_soup.find("meta", attrs={"property": "og:locality"})["content"]
        state = location_soup.find("meta", attrs={"property": "og:region"})["content"]
        zipp = location_soup.find("meta", attrs={"property": "og:postal-code"})[
            "content"
        ]
        country_code = location_soup.find(
            "meta", attrs={"property": "og:country-name"}
        )["content"]
        store_number = location_name.split("#")[-1]
        phone = location_soup.find("meta", attrs={"property": "og:phone_number"})[
            "content"
        ]
        location_type = "<MISSING>"
        latitude = location_soup.find(
            "meta", attrs={"property": "og:location:latitude"}
        )["content"]
        longitude = location_soup.find(
            "meta", attrs={"property": "og:location:longitude"}
        )["content"]

        hours = ""
        days = location_soup.find("dl", attrs={"aria-label": "Store Hours"}).find_all(
            "dt"
        )
        hours_list = location_soup.find(
            "dl", attrs={"aria-label": "Store Hours"}
        ).find_all("dd")

        for x in range(len(days)):
            day = days[x].text.strip()
            hour = hours_list[x].text.strip()
            hours = hours + day + " " + hour + ", "

        hours = hours[:-2]

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=address,
            city=city,
            state=state,
            zip_postal=zipp,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours,
            location_type=location_type,
        )


def scrape():
    log.info(f"Start Crawling {locator_domain} ...")
    result = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in result:
            writer.write_row(rec)
    log.info("Data Grabbing Finished!!")


if __name__ == "__main__":
    scrape()
