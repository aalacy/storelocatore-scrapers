from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
import html
from bs4 import BeautifulSoup as bs


def get_data():
    session = SgRequests(
        dont_retry_status_codes=[404],
    )
    url = "https://www.bricomarche.pl/api/v1/pos/poses.json"
    response = session.get(url).json()

    for location in response["results"]:
        locator_domain = "bricomarche.pl"
        page_url = "https://www.bricomarche.pl/sklep/" + location["Slug"]
        location_name = location["Name"]
        latitude = location["Lat"]
        longitude = location["Lng"]

        if latitude == "0" and longitude == "0":
            continue

        city = location["City"]
        store_number = location["Id"]
        address = html.unescape(location["Street"] + " " + location["HouseNumber"])
        state = html.unescape(location["Province"])
        zipp = location["Postcode"]
        phone = location["Phone"]
        location_type = "<MISSING>"
        country_code = "Poland"

        try:
            hours_response = session.get(page_url)
            hours_response = hours_response.text
        except Exception:
            continue

        hours_soup = bs(hours_response, "html.parser")

        hours_parts = hours_soup.find_all(
            "div", attrs={"class": "b-pos_hoursItemContent"}
        )
        hours = ""
        for part in hours_parts:
            hours = hours + part.text.strip() + ", "
        hours = hours[:-2]
        hours = hours.replace("\n", " ")
        while "  " in hours:
            hours = hours.replace("  ", " ")

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
