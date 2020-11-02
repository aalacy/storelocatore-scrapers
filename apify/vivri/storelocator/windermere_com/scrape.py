from sgscrape.simple_utils import *
from sgscrape.simple_network_utils import *
from sgscrape.simple_scraper_pipeline import *

def fetch_data():
    return fetch_json(
        request_url = "https://svc.moxiworks.com/service/v1/profile/offices/search",
        data_params = {
            "center_lat": 34.014959683598164,
            "center_lon": -118.4117215,
            "order_by": "distance",
            "company_uuid": "1234567",
            "callback": "jQuery22407851157122881546_1596651612792",
            "source": "agent % 20",
            "website": "",
            "source_display_name": "Windermere.com",
            "_": ms_since_epoch()
        },
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cache-control': 'max-age=0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        },
        path_to_locations=['data', 'result_list']
    )

def strip_extension(phone: str):
    return phone.split("x")[0]

def phone_number_extract(raw: str, which_index=0):
    split_phones = raw.split("/")
    try:
        return strip_extension(split_phones[which_index])
    except ValueError:
        return ""

def page_url_from_slug(slug: str):
    return "https://www.windermere.com/offices/" + slug

def scrape():
    """
    The main entrypoint into the program.
    """

    field_definitions = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField("https://windermere.com"),
        page_url = MappingField(mapping = ["url_slug"], value_transform = page_url_from_slug),
        location_name = MappingField(mapping = ['name'], is_required=False),
        street_address = MultiMappingField(mapping = [["location", "address"], ["location", "address2"]]),
        city = MappingField(mapping = ["location", "city"]),
        state = MappingField(mapping = ["location", "state"]),
        zipcode = MappingField(mapping = ["location", "zip"], is_required=False),
        country_code = MappingField(mapping = ["location", "country_code"], is_required=False),
        store_number = MappingField(mapping = ["external_id"], part_of_record_identity=True),
        phone = MappingField(mapping = ["phone"], value_transform = phone_number_extract, is_required=False),
        location_type = MappingField(mapping = ["legal"], is_required=False),
        latitude = MappingField(mapping = ["location", "latitude"], is_required=False),
        longitude = MappingField(mapping = ["location", "longitude"], is_required=False),
        hours_of_operation = MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name = "windermere.com",
                                     data_fetcher= fetch_data,
                                     field_definitions = field_definitions,
                                     fail_on_outlier = False)

    pipeline.run()

if __name__ == "__main__":
    scrape()
