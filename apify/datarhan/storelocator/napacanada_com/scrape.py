import csv
import json
from lxml import etree
from urllib.parse import urljoin
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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


def load_initial_page(driver):
    driver.get("https://www.napacanada.com")
    driver.execute_script('window.open("https://www.napacanada.com")')

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "header-branding-logo"))
    )


def get(url, driver):
    return driver.execute_async_script(
        f"""
        var done = arguments[0]
        fetch("{url}")
            .then(res => res.text())
            .then(done)
    """
    )


def extract_details(html):
    loc_dom = etree.HTML(html)
    scripts = loc_dom.xpath('//script[@type="application/ld+json"]/text()')

    for script in scripts:
        if "address" in script:
            return json.loads(script)


def fetch_data():
    # Your scraper here
    items = []

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
    with SgChrome(is_headless=True, user_agent=user_agent).driver() as driver:
        load_initial_page(driver)

        start_url = "https://www.napacanada.com/en/store-finder?q=H1N+3E2&page=7"
        html = get(start_url, driver)
        dom = etree.HTML(html)

        DOMAIN = "napacanada.com"

        all_locations = dom.xpath('//li[@class="aadata-store-item"]')

        for poi_html in all_locations:
            store_url = poi_html.xpath('.//a[@class="storeWebsiteLink"]/@href')[0]
            store_url = urljoin(start_url, store_url)
            html = get(store_url, driver)
            poi = extract_details(html)

            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["address"]["addressCountry"]
            store_number = poi["@id"]
            phone = poi["telephone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hoo = []
            for elem in poi["openingHoursSpecification"]:
                day = elem["dayOfWeek"][0]
                opens = elem["opens"]
                closes = elem["closes"]
                hoo.append(f"{day} {opens} - {closes}")
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            item = [
                DOMAIN,
                store_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]

            items.append(item)

        return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
