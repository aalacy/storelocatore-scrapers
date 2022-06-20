from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs
import re
import unidecode
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    url = "https://www.centrehifi.com/en/store-locator/"
    class_name = "popup-language-header"

    with SgChrome(
        block_third_parties=False,
    ) as driver:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        response = driver.page_source

    soup = bs(response, "html.parser")

    grids = soup.find_all("div", attrs={"class": "js-single-store-info"})

    for grid in grids:
        locator_domain = "centrehifi.com"
        page_url = "https://www.centrehifi.com/en/store-locator/"
        location_name = grid.find("h3").text.strip()
        latitude = grid["data-store-lat"]
        longitude = grid["data-store-lng"]

        address_parts = grid.find("p", attrs={"class": "p-0 m-0"}).text.strip()
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
        address = address.strip()
        store_number = grid["data-store-id"]
        location_type = ""
        country_code = "CA"

        if "," == address[-1]:
            address = address[:-1]

        phone_test = grid.find_all("a")
        for test in phone_test:
            if "tel:" in test["href"]:
                phone = test["href"].replace("tel:", "")
                break

        hours = ""
        hours_parts = (
            grid.find("div", attrs={"class": "opening-hours"})
            .find("tbody")
            .find_all("tr")
        )

        for part in hours_parts:
            hours = (
                hours
                + part.text.strip()
                .replace("\n", " ")
                .replace("\r", " ")
                .replace("\t", " ")
                + ", "
            )

        hours = unidecode.unidecode(hours[:-2])

        yield {
            "locator_domain": locator_domain,
            "page_url": page_url,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "street_address": address,
            "state": state,
            "zip": zipp,
            "store_number": store_number,
            "phone": phone,
            "location_type": location_type,
            "hours": hours,
            "country_code": country_code,
        }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"]),
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


if __name__ == "__main__":
    scrape()
