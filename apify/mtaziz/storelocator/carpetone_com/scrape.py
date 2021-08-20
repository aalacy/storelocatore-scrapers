from sgrequests import SgRequests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from sglogging import SgLogSetup
from sgselenium import SgChrome
import csv
import json
import time
from lxml import html
from random import randint

logger = SgLogSetup().get_logger("carpetone_com")
driver = SgChrome().driver()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()
url_base_map = "https://flooring.carpetone.com/"
driver.get(url_base_map)
time.sleep(randint(5, 10))
WebDriverWait(driver, 40).until(
    EC.element_to_be_clickable(
        (By.XPATH, "//div[@id='start-geocoder']/div[2]/input[@type='text']")
    )
).click()
logger.info("___________Sleeping for a few seconds_______________")

driver.find_element_by_xpath(
    "//div[@id='start-geocoder']/div[2]/input[@type='text']"
).send_keys("alaska")
time.sleep(randint(8, 10))

# Wait until search button becomes visible
WebDriverWait(driver, 40).until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            "//div[@id='start-geocoder']/div[2]/div/span[2]/button[@class='btn-search']",
        )
    )
).click()
time.sleep(randint(60, 120))  # The site heavy
for i in range(1):
    # Try to zoom out to load all results as in this case, we click on Zoom Out once
    try:
        zoom_out = driver.find_element_by_xpath('//button[(@aria-label="Zoom Out")]')
        time.sleep(randint(30, 40))
        driver.execute_script("arguments[0].click();", zoom_out)
        time.sleep(randint(i + 40, i + 60))
    except:
        pass

time.sleep(randint(5, 8))
raw_data = html.fromstring(driver.page_source)
all_urls = raw_data.xpath(
    '//div[@id="location-list"]/ul/li/div/div/div/div/strong/a/@href'
)
locator_domain_url = "carpetone.com"


def fetch_data():
    items = []
    url_flooring_base = "https://flooring.carpetone.com"
    for url_store in all_urls:
        url_store = (
            url_flooring_base + url_store
            if url_flooring_base not in url_store
            else url_store
        )
        r = session.get(url_store)
        time.sleep(randint(5, 5))
        data_raw = html.fromstring(r.text, "lxml")
        data_type_json = data_raw.xpath('//script[@type="application/ld+json"]/text()')
        data_type_json = data_type_json[0].split("\n")[1]
        data = json.loads(data_type_json)
        locator_domain = locator_domain_url
        page_url = data["url"] or "<MISSING>"
        location_name = "".join(data_raw.xpath("//title/text()"))
        location_name = location_name.split("|")[0] if location_name else "<MISSING>"
        street_address = "".join(data_raw.xpath('//div[@class="street"]/text()'))
        street_address = (
            " ".join(street_address.split()) if street_address else "<MISSING>"
        )
        data_address = data["containedInPlace"]["address"]
        city = data_address["addressLocality"] or "<MISSING>"
        state = data_address["addressRegion"] or "<MISSING>"
        country_code = data_address["addressCountry"] or "<MISSING>"
        zip = data_address["postalCode"] or "<MISSING>"
        store_number = data["branchCode"]
        store_number = store_number.strip() if store_number else "<MISSING>"
        phone_data = data_raw.xpath('//div[@class="telephone"]/a/span/text()')
        phone = "".join(phone_data) or "<MISSING>"
        location_type = data["@type"] or "<MISSING>"
        latitude = data["geo"]["latitude"] or "<MISSING>"
        longitude = data["geo"]["longitude"] or "<MISSING>"
        hoo = data["openingHours"]
        hours_of_operation = "; ".join(hoo) if hoo else "<MISSING>"
        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        items.append(row)
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
