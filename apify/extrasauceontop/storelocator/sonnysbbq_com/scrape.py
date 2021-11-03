from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import json
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


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
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def get_data():
    url = "https://api.sonnysbbq.com/api/v1/locations.bystate"
    driver = get_driver(url)

    soup = bs(driver.page_source, "html.parser")
    object_response = soup.find("body").text.strip()

    response = json.loads(object_response)
    search_states = response.keys()

    for search_state in search_states:
        for location in response[search_state]:
            locator_domain = "sonnysbbq.com"
            page_url = "https://www.sonnysbbq.com/locations/" + location[
                "post_title"
            ].lower().replace(".", "").replace(" - ", " ").replace(" ", "-").replace(
                ",", ""
            )
            location_name = location["post_title"]

            if len(location["acf"]["address"]["address"].split(",")) < 3:
                address_parts = location["acf"]["address"]["address"].replace(",", "")
                address_parts = address_parts.split(" ")[:-3]
                address = ""
                for part in address_parts:
                    address = address + part + " "

                address = address[:-1]

                city = address_parts = location["acf"]["address"]["address"].split(" ")[
                    -3
                ]
                state = address_parts = location["acf"]["address"]["address"].split(
                    " "
                )[-2]
                zipp = address_parts = location["acf"]["address"]["address"].split(" ")[
                    -1
                ]

            else:
                address = location["acf"]["address"]["address"].split(", ")[0]
                city = location["acf"]["address"]["address"].split(", ")[1]
                try:
                    state = location["acf"]["address"]["address"].split(", ")[2]
                    zipp = location["acf"]["address"]["address"].split(", ")[3]

                except Exception:
                    state = (
                        location["acf"]["address"]["address"]
                        .split(", ")[2]
                        .split(" ")[0]
                    )
                    zipp = (
                        location["acf"]["address"]["address"]
                        .split(", ")[2]
                        .split(" ")[1]
                    )

                if len(state.split(" ")) == 2:
                    zipp = state.split(" ")[1]
                    state = state.split(" ")[0]

            if zipp == "United States":
                zipp = "<MISSING>"

            country_code = "US"
            store_number = location["id"]
            try:
                phone = location["catering_phone_number"]

            except Exception:
                phone = location["contact_phone"]

            if phone == "":
                phone = location["contact_phone"]
            location_type = "<MISSING>"
            latitude = location["address"]["lat"]
            longitude = location["address"]["lng"]

            hours = (
                location["store_hours"]
                .replace(
                    "Open for dine-in, takeout & delivery:<br />\r\n<br />\r\n", ""
                )
                .replace("<br />\r\n", ", ")
                .replace("Open for dine-in, takeout and delivery:, , ", "")
                .replace("Open for dine-in, takeout or delivery:, , ", "")
            )

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
