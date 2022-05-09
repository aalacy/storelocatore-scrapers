import ssl
import time

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import sglog

from sgselenium.sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger("olimpica_com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.olimpica.com/nuestras-tiendas"

    locator_domain = "https://www.olimpica.com/"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    time.sleep(2)
    driver.find_element_by_class_name("css-1wy0on6").click()
    time.sleep(1)

    city_list = driver.find_elements_by_css_selector(".flex.self-center.pr3.w1")[1:]
    search_button = driver.find_element_by_class_name("ml4")

    for i, city_item in enumerate(city_list):
        driver.find_element_by_class_name("css-1wy0on6").click()
        time.sleep(1)

        try:
            city_list = driver.find_elements_by_css_selector(
                ".flex.self-center.pr3.w1"
            )[1:]
            time.sleep(1)
            city_item = city_list[i]
        except:
            driver.find_element_by_class_name("css-1wy0on6").click()
            time.sleep(1)
            city_list = driver.find_elements_by_css_selector(
                ".flex.self-center.pr3.w1"
            )[1:]
            time.sleep(1)
            city_item = city_list[i]
        driver.execute_script("arguments[0].click();", city_item)
        search_button.click()
        time.sleep(2)
        base = BeautifulSoup(driver.page_source, "lxml")

        items = base.find_all(class_="relative olimpica-our-shops-0-x-card")
        city = base.find(class_="css-dvua67-singleValue").text
        log.info(city)

        for item in items:
            location_name = item.h3.text.strip()
            street_address = item.p.text.strip()
            state = ""
            zip_code = ""
            country_code = "CO"
            store_number = ""
            location_type = ""
            phone = ""
            hours_of_operation = base.find(
                class_="olimpica-our-shops-0-x-cardSchedule"
            ).get_text(" ")
            latitude = ""
            longitude = ""
            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=base_link,
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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
