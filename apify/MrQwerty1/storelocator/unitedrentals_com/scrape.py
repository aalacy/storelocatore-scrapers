import time
import csv
import json

from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager

from sglogging import sglog

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "unitedrentals.com"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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
        except Exception:
            driver.quit()
            if x == 5:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


# As selenium so cleaning HTML tags to get solid JSON
def getJsonObj(html_string):
    html_string = (
        html_string.replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .replace("</pre></body></html>", "")
    )
    return html_string


def fetch_data():
    out = []
    api_url = "https://www.unitedrentals.com/api/v2/branches"

    driver = get_driver(api_url)
    response = driver.page_source
    jsonobj = getJsonObj(response.split('pre-wrap;">')[1])
    jsonData = json.loads(jsonobj)
    js = jsonData["data"]

    s = set()
    for j in js:
        locator_domain = DOMAIN
        page_url = f'https://www.unitedrentals.com{j.get("url")}'
        location_name = j.get("name").strip()
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"
        store_number = j.get("branchId") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if phone == "00":
            phone = "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        start = j.get("weekdayHours").get("open")
        close = j.get("weekdayHours").get("close")
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for d in days:
            if d.startswith("sat") or d.startswith("sun") or not start:
                _tmp.append(f"{d.capitalize()}: Closed")
            else:
                _tmp.append(f"{d.capitalize()}: {start} - {close}")

        hours_of_operation = ";".join(_tmp)

        if hours_of_operation.count("Closed") == 7:
            continue

        line = (street_address, city, state, postal)
        if line in s:
            continue

        s.add(line)
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
    log.info("Scraping Started")
    start = time.time()
    data = fetch_data()
    write_output(data)
    end = time.time()
    log.info(f"Total Locations added = {len(data)}")
    log.info(f"It took {end-start} seconds to complete the crawl.")


if __name__ == "__main__":
    scrape()
