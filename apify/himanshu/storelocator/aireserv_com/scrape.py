from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


def fetch_locations(base_url):
    with SgChrome(seleniumwire_auto_config=False).driver() as driver:
        driver.set_script_timeout(30)
        driver.get(base_url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "CorporateHeader"))
        )

        locations_url = base_url + "/locations/?CallAjax=GetLocations"

        stores = driver.execute_async_script(
            f"""
            var done = arguments[0]

            return fetch("{locations_url}", {{
                "method": "POST"
            }})
            .then(res => res.json())
            .then(done)
        """
        )

    return stores


def fetch_data():
    base_url = "https://www.aireserv.com"
    stores = fetch_locations(base_url)

    for store_data in stores:
        if store_data["Country"] != "USA" or store_data["ComingSoon"]:
            continue

        locator_domain = "https://www.aireserv.com"
        location_name = store_data["FriendlyName"]
        try:
            street_address = (
                store_data["Address1"].replace("Rome,GA,", "").strip()
                + " "
                + store_data["Address2"]
            )
        except:
            street_address = store_data["Address1"]
        city = store_data["City"]
        state = store_data["State"]
        postal = store_data["ZipCode"].strip()
        country_code = "US"
        store_number = store_data["FranchiseLocationID"]
        phone = store_data["Phone"]
        latitude = store_data["Latitude"]
        longitude = store_data["Longitude"]
        hours_of_operation = (
            store_data["LocationHours"] if store_data["LocationHours"] else "<MISSING>"
        )
        page_url = base_url + store_data["Path"]

        yield SgRecord(
            locator_domain=locator_domain,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            page_url=page_url,
        )


if __name__ == "__main__":
    data = fetch_data()
    write_output(data)
