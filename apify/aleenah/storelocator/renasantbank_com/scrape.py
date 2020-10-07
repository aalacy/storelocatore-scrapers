from sgscrape.simple_network_utils import *
from sgscrape.simple_scraper_pipeline import *
from sgscrape.webdriver import SgChromeDriver
from sgscrape.simple_cache import MemoCache
from typing import *

driver = SgChromeDriver()
cache = MemoCache()

def headers_for_slug(slug: str):
    return cache.memoize(slug, lambda: driver.get_default_headers_for(f'https://locations.renasantbank.com/wp-json/wp/v2/{slug}'))

hour_type = ['Lobby Hours', 'Drive-Up Hours']

def extract_hours(hours_ar: list) -> str:
    result = []
    for idx, hours_inner in enumerate(hours_ar):
        if hours_inner:
            hours_by_type = [f'{hours["days"]}: {hours["open_time"]} - {hours["closing_time"]}' for hours in hours_inner]
            result.append(f'{hour_type[idx]}: {", ".join(hours_by_type)}')
    return ', '.join(result)

def parse_location_type(location_types: Dict[int, str], loc_types: List[int]) -> str:
    return ', '.join([location_types[loc_t] for loc_t in loc_types])

def fetch_from_wp(url_slug: str, page: int) -> List[dict]:
    results = fetch_json(request_url=f'https://locations.renasantbank.com/wp-json/wp/v2/{url_slug}',
                         query_params={
                             'per_page': 100,
                             '_embed': '',
                             'page': page
                         },
                         headers=headers_for_slug(url_slug),
                         path_to_locations=[])

    for res_arr in results:
        for res in res_arr:
            yield res

def fetch_states(page: int) -> List[dict]:
    for item in fetch_from_wp(url_slug='states', page=page):
        yield item

def fetch_cities(page:int) -> List[dict]:
    for item in fetch_from_wp(url_slug='cities', page=page):
        yield item

def fetch_location_types(page: int) -> List[dict]:
    for item in fetch_from_wp(url_slug='location_types', page=page):
        yield item

def fetch_records(page: int) -> List[dict]:
    for item in fetch_from_wp(url_slug='locations', page=page):
        yield item

def scrape():
    # caching the cities and states in id->name dictionaries
    cities = dict([(c['id'], c['name']) for c in paginated(fetch_results=fetch_cities, max_per_page=100, first_page=1)])
    states = dict([(c['id'], c['name']) for c in paginated(fetch_results=fetch_states, max_per_page=100, first_page=1)])
    location_types = dict([(c['id'], c['name']) for c in paginated(fetch_results=fetch_location_types, max_per_page=100, first_page=1)])

    field_definitions = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField("https://renasantbank.com"),
        page_url=MappingField(mapping=['link']),
        location_name=MappingField(mapping=['title', 'rendered'], value_transform=urllib.parse.unquote),
        street_address=MappingField(mapping=['acf', 'street_address']),
        city=MappingField(mapping=['cities'], raw_value_transform=lambda x: cities[x[0][0]]),
        state=MappingField(mapping=['states'], raw_value_transform=lambda x: states[x[0][0]]),
        zipcode=MappingField(mapping=['acf', 'zip_code']),
        country_code=ConstantField('US'),
        store_number=MappingField(mapping=['id'], part_of_record_identity=True),
        phone=MappingField(mapping=['acf','phone_number'], is_required=False),
        location_type=MappingField(mapping=['location_types'], raw_value_transform=lambda x: parse_location_type(location_types, x[0])),
        latitude=MappingField(mapping=['acf', 'latitude']),
        longitude=MappingField(mapping=['acf', 'longitude']),
        hours_of_operation=MultiMappingField(mapping=[['acf','lobby_hours'],['acf','drive_up_hours']],
                                             raw_value_transform=extract_hours,
                                             is_required=False)
    )

    pipeline = SimpleScraperPipeline(scraper_name="renasantbank.com",
                                     data_fetcher=lambda: paginated(fetch_results=fetch_records, max_per_page=100, first_page=1),
                                     field_definitions=field_definitions,
                                     fail_on_outlier=False)

    pipeline.run()

if __name__ == "__main__":
    scrape()