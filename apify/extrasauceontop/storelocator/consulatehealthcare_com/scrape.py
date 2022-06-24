from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    session = SgRequests()
    url = "https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token=YNDRAXWGIEKBMEAP&country=US&multi_account=false"
    response = session.get(url).json()

    for location in response["locations"]:
        locator_domain = "centers.consulatehealthcare.com"
        page_url = "https://centers.consulatehealthcare.com" + location["llp_url"]
        address = location["store_info"]["address"]
        city = location["store_info"]["locality"]
        state = location["store_info"]["region"]
        zipp = location["store_info"]["postcode"]
        location_type = "<MISSING>"
        hours = "24/7"
        country_code = location["store_info"]["country"]

        api_url = (
            "https://api.momentfeed.com/v1/analytics/api/llp.json?address="
            + address.replace(" ", "+")
            + "&locality="
            + city.replace(" ", "+")
            + "&multi_account=false&pageSize=30&region="
            + state
            + "&auth_token=YNDRAXWGIEKBMEAP"
        )
        page_response = session.get(api_url).json()

        phone = page_response[0]["store_info"]["phone"]
        location_name = page_response[0]["store_info"]["name"]
        latitude = page_response[0]["store_info"]["latitude"]
        longitude = page_response[0]["store_info"]["longitude"]
        store_number = page_response[0]["store_info"]["corporate_id"]

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
