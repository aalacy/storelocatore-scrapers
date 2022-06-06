import time

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

from sgselenium.sgselenium import SgFirefox

from selenium.webdriver.common.by import By
from sglogging import sglog
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

domain = "doitbest.com"
log = sglog.SgLogSetup().get_logger(domain)


def fetch_data():
    with SgFirefox(is_headless=True) as driver:
        driver.get("https://doitbest.com/store-locator")
        time.sleep(15)
        inputState = driver.find_element(
            By.XPATH, '//*[@id="StoreLocatorForm_Location"]'
        ).clear()
        inputState = driver.find_element(
            By.XPATH, '//*[@id="StoreLocatorForm_Location"]'
        )
        inputState.send_keys("TX")
        time.sleep(5)
        element = driver.find_element(
            By.XPATH, '//*[@id="StoreLocatorForm_Range"]/option[4]'
        )
        driver.execute_script("arguments[0].setAttribute('value', '1700')", element)
        applyButton = driver.find_element(By.XPATH, "//input[@value='Filter']")
        driver.execute_script("arguments[0].click();", applyButton)
        time.sleep(50)
        all_locations = []
        for request in driver.requests:
            if request.response:
                if request.method == "POST" and "StoreLocator/Submit" in request.url:
                    log.info(request.method + ": " + request.url)
                    log.info(f"Status: {request.response.status_code}")
                    data = json.loads(request.response.body)

                    all_locations += data["Response"]["Stores"]
                    log.info(f" Total Location: {len(all_locations)}")
                    time.sleep(30)
                    for poi in all_locations:
                        store_url = poi["WebsiteURL"]
                        store_url = "https://" + store_url if store_url else "<MISSING>"
                        try:
                            location_name = poi["Name"]
                        except TypeError:
                            continue
                        location_name = location_name if location_name else "<MISSING>"
                        street_address = poi["Address1"]
                        if poi["Address2"]:
                            street_address += ", " + poi["Address2"]
                        street_address = (
                            street_address if street_address else "<MISSING>"
                        )
                        city = poi["City"]
                        city = city if city else "<MISSING>"
                        state = poi["State"]
                        state = state if state else "<MISSING>"
                        zip_code = poi.get("ZipCode")
                        zip_code = zip_code if zip_code else "<MISSING>"
                        country_code = "<MISSING>"
                        store_number = poi["ID"]
                        store_number = store_number if store_number else "<MISSING>"
                        phone = poi["Phone"]
                        phone = phone if phone else "<MISSING>"
                        location_type = "<MISSING>"
                        latitude = poi["Latitude"]
                        latitude = latitude if latitude else "<MISSING>"
                        longitude = poi["Longitude"]
                        longitude = longitude if longitude else "<MISSING>"
                        hours_of_operation = "<MISSING>"

                        item = SgRecord(
                            locator_domain=domain,
                            page_url=store_url,
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

                        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
