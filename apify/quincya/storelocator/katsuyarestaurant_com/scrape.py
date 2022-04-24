import json
import re
import ssl
import time

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sglogging import SgLogSetup

from sgselenium.sgselenium import SgChrome

logger = SgLogSetup().get_logger("katsuyarestaurant.com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    base_link = "https://www.katsuyarestaurant.com/locations"

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)

    base = BeautifulSoup(driver.page_source, "lxml")

    locator_domain = "katsuyarestaurant.com"

    scripts = base.find_all("script", attrs={"type": "application/ld+json"})
    for script in scripts:
        store = json.loads(script.contents[0])

        location_name = store["name"]
        street_address = store["address"]["streetAddress"].replace(" -", ",")
        city = store["address"]["addressLocality"]
        country_code = ""
        try:
            state = store["address"]["addressRegion"]
            zip_code = store["address"]["postalCode"]
            country_code = "US"
        except:
            state = ""
            zip_code = ""
            if "Baha" in street_address:
                country_code = "Bahamas"
        store_number = ""
        location_type = ""
        try:
            phone = store["telephone"]
        except:
            phone = ""
        try:
            hours_of_operation = " ".join(store["openingHours"])
        except:
            hours_of_operation = ""

        link = "https://www.katsuyarestaurant.com/" + city.replace(
            "New York", "manhattan-west"
        ).lower().replace(" ", "-")
        if "miami" in link:
            link = "https://www.sbe.com/restaurants/katsuya/south-beach"
        if "nassau" in link:
            link = "https://www.sbe.com/restaurants/katsuya/baha-mar"
        if "dubai" in link:
            link = "https://www.sbe.com/restaurants/katsuya/dubai"

        logger.info(link)

        driver.get(link)
        time.sleep(2)

        WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.TAG_NAME, "section"))
        )
        time.sleep(2)

        base = BeautifulSoup(driver.page_source, "lxml")

        latitude = ""
        longitude = ""
        try:
            raw_data = base.find(id="popmenu-apollo-state").contents[0]
            js = raw_data.split("STATE =")[1].strip()[:-1]
            store_data = json.loads(js)

            for loc in store_data:
                if "RestaurantLocation:" in loc:
                    store = store_data[loc]
                    try:
                        if street_address in store["streetAddress"]:
                            latitude = store["lat"]
                            longitude = store["lng"]
                            store_number = store["id"]
                            break
                    except:
                        pass
        except:
            pass

        if "sbe.com" in link:
            location_name = base.title.text.split("|")[0].strip()
            if "dining" in location_name.lower():
                location_name = base.title.text.split("|")[1].strip()
            hours_of_operation = (
                " ".join(list(base.find(class_="card__hours-details").stripped_strings))
                .replace("Hours", "")
                .split("We apol")[0]
                .split("Dragon")[0]
                .split("*")[0]
                .strip()
            )
            latitude = (
                re.findall(r'lat":.+[0-9]{2}\.[0-9]+', str(base))[0]
                .split(":")[1]
                .split(",")[0]
            ).replace('"', "")
            longitude = (
                re.findall(r'lng":.+[0-9]{2}\.[0-9]+', str(base))[0]
                .split(":")[1]
                .split(",")[0]
            ).replace('"', "")
        else:
            try:
                location_name = base.h4.text.strip()
            except:
                continue

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )

    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
