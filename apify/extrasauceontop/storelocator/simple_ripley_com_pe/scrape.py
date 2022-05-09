from webdriver_manager.chrome import ChromeDriverManager
from sgselenium.sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    url = "https://ripleyperu.zendesk.com/hc/es/articles/360055893632-Conoce-nuestros-horarios-de-Tienda-Ripley"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    with SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent=user_agent,
        is_headless=True,
    ).driver() as driver:
        driver.get(url)
        response = driver.page_source

    soup = bs(response, "html.parser")
    grids = soup.find_all("div", attrs={"class": "accordion__item"})
    for grid in grids:
        if len(grid.find_all("div", attrs={"class": "accordion__item"})) != 0:
            continue
        city = grid.find("button").text.strip()
        u_lists = grid.find_all("ul")
        for location in u_lists:
            locator_domain = "simple.ripley.com.pe"
            page_url = "https://ripleyperu.zendesk.com/hc/es/articles/360055893632-Conoce-nuestros-horarios-de-Tienda-Ripley"
            location_name = location.find("li").text.strip().split(":")[1].strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            store_number = "<MISSING>"
            address = location.find_all("li")[1].text.strip().split(":")[1].strip()
            state = "<MISSING>"
            zipp = "<MISSING>"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            country_code = "PE"
            hours_parts = location.find_all("li")[2:]

            hours = ""
            for part in hours_parts:
                bit = part.text.strip().split(": ")[1].strip()
                hours = hours + bit + ", "

            hours = hours[:-2]

            if hours == "Cerrado temporalmente":
                continue

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
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], part_of_record_identity=True
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
        hours_of_operation=sp.MappingField(
            mapping=["hours"], part_of_record_identity=True
        ),
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
