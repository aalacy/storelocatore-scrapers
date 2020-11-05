from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils


def fetch_data():
    url="https://www.hwy55.com/locations"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

    r = net_utils.fetch_xml(
        root_node_name='body',
        location_node_name='div',
        location_node_properties={'class' : lambda x : x and x.startswith("views-row views-row-")},
        request_url=url,
        headers=headers)
    for j in r:
        yield j
def cleanup(x):
    try:
        x=x.split(' (')[0]
    except:
        pass
    try:
        x=x.split(' -')[0]
    except:
        pass
    return x
def scrape():
    url="https://www.hwy55.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['div class=[views-field, views-field-path]','span class=[field-content]'], value_transform = lambda x : url+x.split('a href=')[1].split(' class=[button]')[0]),
        location_name=MappingField(mapping=['div class=[views-field, views-field-name]','h2 class=[field-content]','h2 class=[field-content]'], value_transform = cleanup),
        latitude=MissingField(),
        longitude=MissingField(),
        street_address=MappingField(mapping=['div class=[views-field, views-field-address]','div class=[field-content]','div class=[location, vcard]','div class=[adr]','div class=[street-address]','div class=[street-address]']),
        city=MappingField(mapping=['div class=[views-field, views-field-address]','div class=[field-content]','div class=[location, vcard]','div class=[adr]','span class=[locality]','span class=[locality]']),
        state=MappingField(mapping=['div class=[views-field, views-field-address]','div class=[field-content]','div class=[location, vcard]','div class=[adr]','span class=[region]','span class=[region]'], is_required = False),
        zipcode=MappingField(mapping=['div class=[views-field, views-field-address]','div class=[field-content]','div class=[location, vcard]','div class=[adr]','span class=[postal-code]','span class=[postal-code]']),
        country_code=ConstantField("US"),
        phone=MappingField(mapping=['div class=[views-field, views-field-address]','div class=[field-content]','div class=[location, vcard]','div class=[adr]','div class=[tel]','span class=[value]','span class=[value]']),
        store_number=MissingField(),
        hours_of_operation=MultiMappingField(mapping=[['div class=[views-field, views-field-field-monday-hours]','div class=[field-content]','div class=[field-content]'],['div class=[views-field, views-field-field-tuesday-hours]','div class=[field-content]','div class=[field-content]'],['div class=[views-field, views-field-field-wednesday-hours]','div class=[field-content]','div class=[field-content]'],['div class=[views-field, views-field-field-thursday-hours]','div class=[field-content]','div class=[field-content]'],['div class=[views-field, views-field-field-friday-hours]','div class=[field-content]','div class=[field-content]'],['div class=[views-field, views-field-field-saturday-hours]','div class=[field-content]','div class=[field-content]'],['div class=[views-field, views-field-field-sunday-hours]','div class=[field-content]','div class=[field-content]']],multi_mapping_concat_with='; '),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='hwy55.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
