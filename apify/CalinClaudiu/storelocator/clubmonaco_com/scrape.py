from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from sgselenium import SgChrome
from selenium.webdriver.common.action_chains import ActionChains
from sglogging import sglog
from bs4 import BeautifulSoup
import json
import time


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="clubmonaco")

    son = []
    with SgChrome() as driver:

        driver.get("https://www.clubmonaco.com/en/StoreLocator")
        actions = ActionChains(driver)
        driver.implicitly_wait(15)
        actions.send_keys(Keys.ESCAPE).perform()
        actions.send_keys(Keys.ESCAPE).perform()
        option = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="dwfrm_storelocator_country-button"]')
            )
        )
        driver.execute_script("arguments[0].click();", option)
        options = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="dwfrm_storelocator_country-menu"]')
            )
        )
        canada = (  # noqa
            WebDriverWait(driver, 30)
            .until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="dwfrm_storelocator_country-menu"]/li/div[text()[contains(.,"anada")]]',
                    )
                )
            )
            .click()
        )  # noqa
        zipcode = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="dwfrm_storelocator_postalCode"]')
            )
        )
        driver.execute_script("arguments[0].value='K1Y 2B8';", zipcode)
        radius = driver.find_element_by_xpath(
            '//*[@id="dwfrm_storelocator_maxdistance"]/option[1]'
        )
        driver.execute_script("arguments[0].value='15000';", radius)
        search = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="dwfrm_storelocator"]/fieldset/div[7]/button')
            )
        )
        driver.execute_script("arguments[0].click();", search)

        wait_for_items = WebDriverWait(driver, 30).until(  # noqa
            EC.visibility_of_element_located((By.XPATH, '//*[@id="List"]/div[1]'))
        )  # noqa
        driver.execute_script("arguments[0].click();", option)  # noqa
        options = WebDriverWait(driver, 30).until(  # noqa
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="dwfrm_storelocator_country-menu"]')
            )
        )  # noqa
        us = (  # noqa
            WebDriverWait(driver, 30)
            .until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="dwfrm_storelocator_country-menu"]/li/div[text()[contains(.,"United States")]]',
                    )
                )
            )
            .click()
        )  # noqa
        zipcode = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="dwfrm_storelocator_postalCode"]')
            )
        )
        driver.execute_script("arguments[0].value='96701';", zipcode)
        radius = driver.find_element_by_xpath(
            '//*[@id="dwfrm_storelocator_maxdistance"]/option[1]'
        )
        driver.execute_script("arguments[0].value='15000';", radius)
        search = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="dwfrm_storelocator"]/fieldset/div[7]/button')
            )
        )
        driver.execute_script("arguments[0].click();", search)
        time.sleep(25)
        for r in driver.requests:
            if (
                "on/demandware.store/Sites-ClubMonaco_US-Site/en_US/Stores-ViewResults"
                in r.path
            ):
                son.append(r.response.body)

    for i in son:
        soup = BeautifulSoup(i, "lxml")
        soup1 = soup.find(
            "div", {"class": lambda x: x and all(i in x for i in ["storeJSON", "hide"])}
        )["data-storejson"]
        soup1 = '{"store":' + soup1 + "}"
        soup = soup.find("script", {"type": "application/ld+json"})
        sson = json.loads(soup.text)
        sony = json.loads(soup1)
        count = 0
        for idex, i in enumerate(sson["store"]):
            if idex % 2 == 0:
                store = {}
                store["main"] = i
                store["sec"] = sson["store"][idex + 1]
                store["tert"] = sony["store"][count]
                if store["main"]["telephone"] != store["tert"]["phone"]:
                    logzilla.info(
                        f"\n !!!!! !!!!! !!!!! \n This store might be incorrectly scraped!! \n {store}"
                    )
                count += 1
                yield store

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_hours(x):
    x = (
        x.replace("</p>\n", "; ")
        .replace("<p>", "")
        .replace("\n", "")
        .replace("</p>", "")
        .replace("<br />", "; ")
        .replace("&nbsp;", " ")
        .replace("</br></br>", "")
        .replace("</br>", "; ")
        .replace(";  ;", ";")
    )
    if "Curb" in x:
        x = "".join(x.split("Curb")[:-1])
    return x


def good_phone(x):
    x = x.replace("-", "")
    if "Curb" in x:
        x = "".join(x.split("Curb")[:-1])
    if "WedSun" in x:
        x = x.replace("WedSun", "")
    return x


def scrape():
    url = "https://clubmonaco.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(mapping=["main", "legalName"]),
        latitude=MappingField(mapping=["tert", "latitude"]),
        longitude=MappingField(mapping=["tert", "longitude"]),
        street_address=MappingField(
            mapping=["sec", "address", "streetAddress"],
            value_transform=lambda x: " ".join(x.split(",")[:-1]),
        ),
        city=MappingField(mapping=["tert", "city"]),
        state=MappingField(mapping=["tert", "stateCode"]),
        zipcode=MappingField(mapping=["tert", "postalCode"]),
        country_code=MappingField(mapping=["sec", "address", "addressCountry"]),
        phone=MappingField(mapping=["tert", "phone"], value_transform=good_phone),
        store_number=MappingField(mapping=["tert", "id"]),
        hours_of_operation=MappingField(
            mapping=["main", "openingHours"], value_transform=fix_hours
        ),
        location_type=MappingField(mapping=["sec", "@type"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="clubmonaco.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=25,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
