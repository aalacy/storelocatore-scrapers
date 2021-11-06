from sgrequests import SgRequests
from sgselenium import SgChrome
import pandas as pd
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import re
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def reset_sessions(data_url):

    s = SgRequests()

    driver = SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ).driver()
    driver.get(data_url)

    incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    incap_url = data_url + incap_str

    s.get(incap_url)

    for request in driver.requests:

        headers = request.headers
        try:
            response = s.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")
            if len(test_html) < 2:
                continue
            else:
                driver.quit()
                return [s, headers, response_text]

        except Exception:
            continue


def get_data():
    response = reset_sessions("https://mezeh.com/locations/")[-1]
    soup = bs(response, "html.parser")

    grids = soup.find_all(
        "div", attrs={"class": "column_attr clearfix align_left mobile_align_left"}
    )
    session = SgRequests()
    for grid in grids:
        locator_domain = "mezeh.com"
        try:
            page_url = grid.find("a")["href"]
        except Exception:
            page_url = "<MISSING>"
        zipp = "nope"
        location_name = grid.find("h4").text.strip()
        print(location_name)
        try:
            address_section = grid.find("a").text.strip().split("\n")[1]
            address_parts = address_section.split(".")
            if len(address_parts) > 1:
                address_parts = address_parts[:-1]
                address = ""
                for part in address_parts:
                    address = address + part + " "
                address = address.strip()
            else:
                address_parts = address_parts[0].split(",")[0].split(" ")[:-1]
                address = ""
                for part in address_parts:
                    address = address + part + " "
                address = address.strip()

            city = address_section.split(" ")[-3].replace(",", "").replace(".", "").strip()
            state = address_section.split(" ")[-2].replace(",", "").replace(".", "").strip()
            zipp = address_section.split(" ")[-1].replace(",", "").replace(".", "").strip()
            country_code = "US"
            store_number = "<MISSING>"

            try:
                phone = grid.text.split("phone")[1].split("hours")[0].replace("\n", "")
            except Exception:
                phone = "<MISSING>"
            
            hours_parts = grid.text.split("hours")[1].split("order")[0].split("\n")
            hours = ""
            for item in hours_parts:
                item = item.replace("\r", "")
                hours = hours + item + " "
            location_type = "<MISSING>"
            hours = hours.strip()

            try:
                latlon_url = grid.find("a", text=re.compile("get directions"))["href"]
                r = session.get(latlon_url).url
                latitude = r.split("@")[1].split(",")[0]
                longitude = r.split("@")[1].split(",")[1]
            except Exception:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
        except Exception:
            if "coming soon" in grid.text.strip():
                address_section = grid.find("h5").text.strip()
                address_parts = address_section.split("phone")[0].split(".")
                if len(address_parts) > 1:
                    address_parts = address_parts[:-1]
                    address = ""
                    for part in address_parts:
                        address = address + part + " "
                    address = address.strip()
                else:
                    address_parts = address_parts[0].split(",")[0].split(" ")[:-1]
                    address = ""
                    for part in address_parts:
                        address = address + part + " "
                    address = address.strip()

                city = (
                    address_section.split(" ")[-3]
                    .replace(",", "")
                    .replace(".", "")
                    .strip()
                    .replace("blvd", "")
                )
                state = (
                    address_section.split(" ")[-2].replace(",", "").replace(".", "").strip()
                )
                zipp = (
                    address_section.split(" ")[-1]
                    .replace(",", "")
                    .replace(".", "")
                    .strip()
                    .split("\n")[0]
                )
                country_code = "US"
                store_number = "<MISSING>"

                if "phone" in grid.text.strip():
                    phone = grid.text.strip().split("phone")[1].split("\n")[1]
                else:
                    phone = "<MISSING>"

                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours = "Coming Soon"

            else:
                address = grid.find("h5").text.strip().split(".")[0]
                city = grid.find("h5").text.strip().split(".")[1].split(",")[0]

                try:
                    state = (
                        grid.find("h5")
                        .text.strip()
                        .split(".")[1]
                        .split(",")[1]
                        .split(" ")[1]
                    )

                    zipp = (
                        grid.find("h5")
                        .text.strip()
                        .split(".")[1]
                        .split(",")[1]
                        .split(" ")[2]
                        .split("\n")[0]
                    )
                    phone = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    hours = "Temporarily Closed"
                    store_number = "<MISSING>"
                    country_code = "US"
                except Exception:
                    address = grid.find("h5").text.strip().split(location_name)[0]
                    city = location_name
                    state = grid.find("h5").text.strip().split(", ")[-1].split(" ")[0]
                    zipp = grid.find("h5").text.strip().split(", ")[-1].split(" ")[1][:5]

                if zipp == "nope":
                    zipp = (
                        grid.find("h5")
                        .text.strip()
                        .split(".")[1]
                        .split(",")[1]
                        .split(" ")[2]
                        .split("\n")[0]
                    )
                phone = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours = "Temporarily Closed"
                store_number = "<MISSING>"
                country_code = "US"

        if "goo.gl" in page_url:
            page_url = "<MISSING>"

        phone = phone.strip().replace("\n", "")
        
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
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
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
            mapping=["store_number"]
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=1000,
    )
    pipeline.run()


scrape()
