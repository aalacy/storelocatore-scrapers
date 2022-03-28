from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    session = SgRequests()

    url = "https://www.metrobyt-mobile.com/self-service-sigma-commerce/v1/store-locator?store-type=AuthorizedDealer&min-latitude=12.7086&max-latitude=71.286&min-longitude=-52.298&max-longitude=-170.371337"

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "accept": "application/json, text/plain, */*",
    }
    response = session.get(url, headers=headers).json()

    for location in response:
        locator_domain = "metrobyt-mobile.com"
        page_url = url
        location_name = "Metro by T-Mobile Authorized Dealer"
        address = location["location"]["address"]["streetAddress"]
        city = location["location"]["address"]["addressLocality"]
        state = location["location"]["address"]["addressRegion"]
        zipp = location["location"]["address"]["postalCode"]
        country_code = "US"
        store_number = location["id"]
        phone = location["telephone"]
        location_type = location["type"]
        latitude = location["location"]["latitude"]
        longitude = location["location"]["longitude"]

        hours = ""

        for section in location["openingHours"]:
            days = section["days"]
            section_hours = section["time"]
            for day in days:
                hours = hours + day + " " + section_hours + ", "

        hours = hours[:-2]

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
