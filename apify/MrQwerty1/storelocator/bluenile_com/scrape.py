import csv
import ssl

from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def get_driver(url, driver=None):
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

            break
        except Exception as e:
            driver.quit()
            if x == 10:
                raise Exception("Failed 10 times for the following reason: " + e)
            continue
    return driver


def get_html():
    url = "https://www.bluenile.com/"
    class_name = "state-name"
    driver = get_driver(url)

    driver.execute_script(
        "window.open('https://www.bluenile.com/jewelry-stores', 'tab2');"
    )
    driver.switch_to.window("tab2")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, class_name))
    )

    response = driver.page_source
    driver.quit()

    return response


def fetch_data():
    out = []
    locator_domain = "https://www.bluenile.com/"

    source = get_html()
    tree = html.fromstring(source)
    divs = tree.xpath("//div[@class='store']")

    for d in divs:
        street_address = (
            "".join(d.xpath(".//span[@itemprop='streetAddress']/text()")).strip()
            or "<MISSING>"
        )
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = (
            "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
            or "<MISSING>"
        )
        state = (
            "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        page_url = (
            "".join(d.xpath(".//a[@class='store-name']/@href")).strip() or "<MISSING>"
        )
        location_name = (
            "".join(d.xpath(".//meta[@itemprop='name']/@content")).strip()
            or "<MISSING>"
        )
        phone = (
            "".join(d.xpath(".//meta[@itemprop='telephone']/@content")).strip()
            or "<MISSING>"
        )
        latitude = "".join(d.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-lng")) or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            ";".join(d.xpath(".//meta[@itemprop='openingHours']/@content")).strip()
            or "Coming Soon"
        )

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    ssl._create_default_https_context = ssl._create_unverified_context
    scrape()
