import csv
from sgselenium import SgSelenium
import re
import time
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

logger = SgLogSetup().get_logger("habitburger_com")


driver = SgSelenium().chrome()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r"ll=[-?\d\.]*\,([-?\d\.]*)", url)[0]
    lat = re.findall(r"ll=(-?[\d\.]*)", url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    page_url = [""]
    types = []

    driver.get("https://www.habitburger.com/locations/all/")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "reglist"))
    )
    uls = driver.find_elements_by_class_name("reglist")
    del uls[-1]  # china
    for ul in uls:
        ast = ul.find_elements_by_tag_name("a")
        for div in ast:
            l = div.get_attribute("href")
            if "/locations/" in l:
                if page_url[-1] != l:
                    page_url.append(l)
    del page_url[0]
    logger.info(len(page_url))

    coming_soon = []
    for url in page_url:
        logger.info(url)
        driver.get(url)
        cs = driver.find_elements_by_id("coming_soon")
        if cs != []:
            coming_soon.append(url)
            continue
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        the_script = soup.find_all("script", {"type": "application/ld+json"})[1]
        the_script = str(the_script)
        logger.info(the_script)

        locs.append(re.findall(r'.*"name": "([^"]*)"', the_script, re.DOTALL)[0])
        types.append(re.findall(r'.*"@type": "([^"]*)"', the_script, re.DOTALL)[0])
        c = re.findall(r'.*"addressLocality": "([^"]*)"', the_script, re.DOTALL)[0]
        cities.append(c)
        s = re.findall(r'.*"addressRegion": "([^"]*)"', the_script, re.DOTALL)[0]
        states.append(s)
        z = re.findall(r'.*"postalCode": "([^"]*)"', the_script, re.DOTALL)[0]
        zips.append(z)
        street.append(
            re.findall(r'.*"streetAddress": "([^"]*)"', the_script, re.DOTALL)[0]
            .replace(z, "")
            .replace(s, "")
            .replace(c, "")
            .strip()
        )
        try:
            t = re.findall(
                r'.*"openingHours": \[.*"([^"]*)".*\],', the_script, re.DOTALL
            )[0]
            if "<br>" in t:
                t = t.replace("<br>", " ")
            if "> " in t:
                t = t.replace("> ", "")
            if t.strip() == ">":
                t = "<MISSING>"
            timing.append(t)
        except:
            timing.append("<MISSING>")
        try:
            phones.append(
                re.findall(r'.*"telephone": "([^"]*)"', the_script, re.DOTALL)[0]
            )
        except:
            phones.append("<MISSING>")

        lat.append(re.findall(r"lat: (-?[\d\.]*),", str(soup), re.DOTALL)[0])
        long.append(re.findall(r"lng: (-?[\d\.]*)", str(soup), re.DOTALL)[0])

    for u in coming_soon:
        del page_url[page_url.index(u)]

    all = []
    logger.info(len(locs))
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.habitburger.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
