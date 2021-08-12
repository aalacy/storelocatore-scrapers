from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import json
import html
import re
import unidecode
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "[":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "]":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(
                        html.unescape(json.loads(html_string[start : end + 1]))
                    )
                except Exception:
                    pass
        count = count + 1

    return json_objects


def get_driver(url, class_name, driver=None):
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
                is_headless=False,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def get_data():
    url = "https://www.centrehifi.com/en/storelocator"
    class_name = "popup-language-header"
    driver = get_driver(url, class_name)

    response = driver.page_source
    driver.quit()

    json_objects = extract_json(response)

    location_lists = []
    for object in json_objects:
        if len(object) > 3:
            location_lists.append(object)

    locations = location_lists[0]
    soup = bs(response, "html.parser")
    grids = soup.find_all("div", attrs={"class": "js-single-store-info"})[
        len(locations) * -1 :
    ]

    x = 0

    for location in locations:
        locator_domain = "centrehifi.com"
        page_url = "<MISING>"
        location_name = location[0]

        address_parts = location[4]
        address_parts = unidecode.unidecode(
            address_parts.lower()
            .replace(", canada", "")
            .replace("centre hifi, ", "")
            .replace("centre hifi ", "")
        )

        if "qc" in address_parts:

            address_pieces = address_parts.split(", qc")[0].split(" ")[:-1]

            if (
                len(address_pieces[-1]) == 2
                and bool(re.search(r"\d", address_pieces[-1])) is False
            ):
                address_pieces = address_pieces[:-1]
                city = (
                    address_parts.split(", qc")[0].strip().split(" ")[-2]
                    + " "
                    + address_parts.split(", qc")[0].strip().split(" ")[-1]
                )

            else:
                city = address_parts.split(", qc")[0].strip().split(" ")[-1]

            address = ""
            for piece in address_pieces:
                address = address + piece + " "

            state = "QC"
            try:
                zipp = address_parts.split(", qc ")[1]
            except Exception:
                zipp = "<MISSING>"

        else:
            address_pieces = address_parts.split(", ")
            if bool(re.search("[a-zA-Z]", address_pieces[0])) is False:
                address = address_pieces[0] + " " + address_pieces[1]

            else:
                address = address_pieces[0]

            if "quebec" in address_parts:
                city = address_parts.split(", ")[-2]
                state = address_parts.split(", ")[-1].strip().split(" ")[0]
                zipp = (
                    address_parts.split(", ")[-1].strip().split(" ")[1]
                    + " "
                    + address_parts.split(", ")[-1].strip().split(" ")[2]
                )

            else:
                city = address_parts.split(", ")[-1].strip().split(" ")[0]
                zipp = (
                    address_parts.split(", ")[-1].strip().split(" ")[-2]
                    + " "
                    + address_parts.split(", ")[-1].strip().split(" ")[-1]
                )
                state = "<MISSING>"

        country_code = "CA"

        store_number = location[3]
        latitude = location[1]
        longitude = location[2]

        grid = grids[x]

        phone = grid.find("a").text.strip()
        location_type = "<MISSING>"

        tds = grid.find_all("td")

        hours = ""
        for td in tds:
            hours = hours + unidecode.unidecode(html.unescape(td.text.strip())) + " "

        hours = hours.strip().replace("h", ":").replace("T:u", "Thu")

        x = x + 1
        address = address.replace(",", "")
        yield {
            "locator_domain": locator_domain,
            "page_url": page_url,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "store_number": store_number,
            "street_address": address,
            "state": state,
            "zip": zipp,
            "phone": phone,
            "location_type": location_type,
            "hours": hours,
            "country_code": country_code,
        }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
