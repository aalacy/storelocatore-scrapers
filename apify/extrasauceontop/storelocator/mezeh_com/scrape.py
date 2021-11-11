from sgrequests import SgRequests
from sgselenium import SgChrome
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
        if "coming soon" in grid.text.strip():
            continue

        locator_domain = "mezeh.com"
        page_url = "https://mezeh.com/locations/"

        location_name = grid.find("h4").text.strip()

        location_data_parts = str(grid).split("\n")
        address_parts = location_data_parts[1]

        address = address_parts.split(">")[1].split("<")[0].strip()
        city = address_parts.split("<br/>")[1].split("<")[0].split(", ")[0]
        state = (
            address_parts.split("<br/>")[1].split("<")[0].split(", ")[1].split(" ")[0]
        )

        try:
            zipp = (
                address_parts.split("<br/>")[1]
                .split("<")[0]
                .split(", ")[1]
                .split(" ")[1]
            )
        except Exception:
            zipp = address_parts.split("<br/>")[1].split("<")[0].split(", ")[-1]

        the_index = 0
        for item in location_data_parts:
            the_index = the_index + 1
            if "phone" in item.lower():
                phone = location_data_parts[the_index].replace("<br/>", "")

        if "hours" in grid.text.strip().lower():
            the_index = 0
            start = ""
            for item in location_data_parts:
                the_index = the_index + 1
                if "hours" in item.lower():
                    start = the_index

                if start != "" and "pm" not in item.lower() and the_index != start:
                    end = the_index - 1
                    break

            hours = ("").join(
                part.replace("\r", "").split("<")[0] + ", "
                for part in location_data_parts[start:end]
            )
            hours = hours[:-2]

        else:
            hours = "<MISSING>"

        try:
            latlon_url = grid.find("a", text=re.compile("get directions"))["href"]
            r = session.get(latlon_url).url
            latitude = r.split("@")[1].split(",")[0]
            longitude = r.split("@")[1].split(",")[1]

        except Exception:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        country_code = "US"

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
        store_number=sp.MappingField(mapping=["store_number"]),
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
