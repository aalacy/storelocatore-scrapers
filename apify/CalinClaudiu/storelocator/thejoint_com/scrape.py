from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import json

def fetch_data():
    url = "https://www.thejoint.com/locations"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
    r = net_utils.fetch_xml(request_url=url,headers=headers,root_node_name='body', location_node_name='script')
    for i in r:
        if 'TJ.Locations.clinics' in str(json.dumps(i)):
            son = json.dumps(i)
    son = son.split('clinics = [')[1]
    son = son.rsplit('];"}',1)[0]
    son ='{"store":['+son+"]}"
    son = son.replace('\\','')
    h = ""
    son = son.split('"geocode_response"')
    
    for i in son:
        try:
            i = i.split(',"phone_1"')[1]
            i = '"phone_1"'+i
            h = h+i
        except:
            h = h+i
        
    son = ''.join(son)
    son = h
    son = son.split('"display_general_information"')
    j = 0
    h = ""
    for i in son:
        try:
            i = i.split(',"is_open"')[1]
            i = '"is_open"'+i
            h = h+i
        except:
            h = h+i
    #,"display_general_information":
    #"is_open"
    #,"doctor_bios"
    son = h
    son = son.split('"doctor_bios"')
    j = 0
    h = ""
    for i in son:
        try:
            i = i.split(',"display_social_icons"')[1]
            i = '"display_social_icons"'+i
            h = h+i
        except:
            h = h+i

    #,"clinic_template_custom"
    #,"hour_start_monday"
    son = h
    son = son.split('"clinic_template_custom"')
    j = 0
    h = ""
    for i in son:
        try:
            i = i.split(',"hour_start_monday"')[1]
            i = '"hour_start_monday"'+i
            h = h+i
        except:
            h = h+i

    #"directional_info"
    son = h
    son = son.split('"directional_info"')
    j = 0
    h = ""
    for i in son:
        try:
            i = i.split(',"latitude"')[1]
            i = '"latitude"'+i
            h = h+i
        except:
            h = h+i
    #"tracking_codes"
    #"landing_page_exclude"
    son = h
    son = son.split('"tracking_codes"')
    j = 0
    h = ""
    for i in son:
        try:
            i = i.split(',"landing_page_exclude"')[1]
            i = '"landing_page_exclude"'+i
            h = h+i
        except:
            h = h+i
    son = json.loads(h)
    for i in son['store']:
        yield i

def pretty_hours(x):
    x = json.dumps(x)
    x = x.replace('{','').replace('}','').replace("'",'').replace('"','')
    return x
def status(x):
    if x=='True':
        return "<MISSING>"
    else:
        return "Closed or Coming Soon"
def scrape():
    url="https://www.thejoint.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url_path'], value_transform = lambda x : "https://www.thejoint.com/"+x),
        location_name=MappingField(mapping=['name'], value_transform = lambda x : x.replace('&#8211;','')),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MultiMappingField(mapping=[['address_1'],['address_2']], multi_mapping_concat_with = ', '),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['state']),
        zipcode=MappingField(mapping=['zip_code']),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['display_phone_1'], is_required = False),
        store_number=MappingField(mapping=['number']),
        hours_of_operation=MappingField(mapping=['display_all_days_hours_ns'], value_transform = pretty_hours),
        location_type=MappingField(mapping=['is_open'], value_transform = status)
    )

    pipeline = SimpleScraperPipeline(scraper_name='thejoint.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
