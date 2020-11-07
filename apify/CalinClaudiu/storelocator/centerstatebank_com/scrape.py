from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgselenium import SgChrome
from selenium.webdriver.common.keys import Keys
import json

def fetch_data():
    with SgChrome() as driver:
        #//*[@id="locations_radius"]/option[4]
        #radius option location
        url = 'https://www.centerstatebank.com/locations/'
        driver.get(url)
        radius = driver.find_element_by_xpath('//*[@id="locations_radius"]/option[4]')
        #finding default radius option by xpath <option value="100" default="" selected="selected">100 Miles</option>
        driver.execute_script("arguments[0].value = '555555';", radius)
        #Changing default radius value from '100' to '555555'
        search = driver.find_element_by_xpath('//*[@id="locations_search"]')
        #Finding search field
        search.send_keys('Ohio')
        #arbitrary location
        search.send_keys(Keys.RETURN)
        #/html/body/script[2]
        #json location
        k = driver.find_element_by_xpath('/html/body/script[2]').get_attribute('innerHTML')
        k = k.split('locationsData = {')[1]
        k = k.split('[',1)[1]
        k = k.split(']};')[0]
        k = '{"stores":['+k+']}'
        #magic
        son = json.loads(k)
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
        for i in son['stores']:
            suburl = i['properties']['permalink']
            r = net_utils.fetch_xml(
                root_node_name='body',
                location_node_name='div',
                location_node_properties={'class': lambda x : x and x.startswith("location__hours-day location__hours-day--")},
                request_url=suburl,
                headers=headers)
            i['hours']=[]
            for j in r:
                if j[list(j)[0]]!='Appointment Only':
                    i['hours'].append(j['strong']['strong'])
                    i['hours'].append(': '+j[list(j)[0]]+'; ')
                    #almost fixexs this case: https://www.centerstatebank.com/location/osprey-branch/154/
            if len(i['hours'])>0:
                if i['hours'][0]=='Saturday':
                    i['hours'].pop(0)
                    i['hours'].pop(0)
                    i['hours'].pop(0)
                    i['hours'].pop(0)
                    i['hours'].pop(0)
                    i['hours'].pop(0)
                    i['hours'] = ''.join(i['hours'][0:14])
                    #cleanup for case above + "today" schedule
                else:
                    i['hours'].pop(0)
                    i['hours'].pop(0)
                    i['hours'] = ''.join(i['hours'][0:14])
                    #cleanup for "today schedule
                #cleanup for case where two sets of hours are displayed, lobby and drive-thru
                #example: https://www.centerstatebank.com/location/indiantown-branch/158/
                #Takes lobby hours if available,else drive-thru hours.
            else:
                i['hours']="<MISSING>"
            #cleanup when hours missing entirely              
            yield i


def parse_features(x):
    s=[]
    for i in x.split("'value': '"):
        s.append(i.split("', 'label'")[0])

    s.pop(0)
    s = ', '.join(s)
    s = s.replace(')',' ')
    return s
            
         
def scrape():
    url="https://www.centerstatebank.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['properties','permalink']),
        location_name=MappingField(mapping=['properties','name']),
        latitude=MappingField(mapping=['geometry','coordinates',1]),
        longitude=MappingField(mapping=['geometry','coordinates',0]),
        street_address=MultiMappingField(mapping=[['properties','address','line1'],['properties','address','line2']], multi_mapping_concat_with = ', '),
        city=MappingField(mapping=['properties','address','city']),
        state=MappingField(mapping=['properties','address','region']),
        zipcode=MappingField(mapping=['properties','address','postalCode']),
        country_code=MappingField(mapping=['properties','address','countryCode']),
        phone=MappingField(mapping=['properties','phone']),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['hours']),
        location_type=MappingField(mapping=['properties','features'], value_transform = parse_features, is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='centerstatebank.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
