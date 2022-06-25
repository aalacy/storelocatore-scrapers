from sgselenium import SgFirefox
from bs4 import BeautifulSoup as bs
import ssl
import html
from sgscrape import simple_scraper_pipeline as sp
import unidecode

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    url = "https://www.bhv.fr/magasins"
    with SgFirefox(
        is_headless=True, block_third_parties=False, proxy_country="fr"
    ) as driver:
        driver.get(url)
        response = driver.page_source

        soup = bs(response, "html.parser")
        page_urls = [
            "https://www.bhv.fr" + href["value"]
            for href in soup.find("select", attrs={"name": "storeselect"}).find_all(
                "option"
            )[1:]
        ]

        for page_url in page_urls:
            driver.get(page_url)
            page_response = unidecode.unidecode(html.unescape(driver.page_source))
            page_soup = bs(page_response, "html.parser")

            locator_domain = "www.bhv.fr"
            location_name = page_soup.find(
                "h1", attrs={"class": "page-title"}
            ).text.strip()
            latitude = page_soup.find("div", attrs={"id": "store-map"})["lat"]
            longitude = page_soup.find("div", attrs={"id": "store-map"})["lng"]

            address_parts = page_soup.find(
                "div", attrs={"class": "info-block-value"}
            ).find_all("p")
            address_index = 0
            for part in address_parts:
                if "paris" in part.text.lower():
                    break

                if "tel" in part.text.lower():
                    address_index = address_index - 1
                    break
                address_index = address_index + 1

            if address_index == 1:
                address = address_parts[0].text.strip()
                city = "".join(
                    thing + " "
                    for thing in address_parts[1].text.strip().split(" ")[1:]
                )
                zipp = address_parts[1].text.strip().split(" ")[0]
                phone = address_parts[2].text.strip().split(":")[-1].strip()

            elif address_index == 0:
                address_bits = address_parts[0].text.strip().replace("\n", " ")
                address = address_bits.split("75004")[0]
                zipp = "75004"
                city = "PARIS"
                phone = address_parts[1].text.strip().split(":")[-1].strip()

            hours = (
                page_soup.find("div", attrs={"class": "info-block-schedule-value"})
                .find("p")
                .text.strip()
            )

            store_number = "<MISSING>"
            location_type = "<MISSING>"
            country_code = "FR"
            state = "<MISSING>"
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
