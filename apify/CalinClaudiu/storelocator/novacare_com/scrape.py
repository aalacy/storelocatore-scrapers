from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
import json
def pretty_hours(x):
    x = x.replace('</td><td>',' ')
    x = x.replace('</tr>',', ')
    x = x.replace('<tr>','')
    x = x.replace('<td>','')
    x = x.replace('</td>','')
    if len(x)<3:
        x = "<MISSING>"
    return x
    
def parse_html(x):
    k = {}
    j = []
    add = x.split('loc-result-card-address-container')[1].split("'_blank\'>")[1].split('</a>',1)[0]
    #name
    try:
        k['name'] = x.split('loc-result-card-name')[1].split('<a href=')[1].split('>')[1].split('<',1)[0]
    except:
        k['name'] = "<MISSING>"
    #street address
    try:
        k['address'] = add.split('<br/>')
        for i in k['address']:
            if i.count(',')!=1:
                j.append(i)
        k['address'] = ','.join(j)
    except:
        k['address'] = "<MISSING>"

    #city
    try:
        k['city'] = add.split('<br/>')[-1].split(',',1)[0]
    except:
        k['city'] = "<MISSING>"

    #state
    try:
        k['state'] = add.split('<br/>')[-1].split(',',1)[1].split(' ')[1]
    except:
        k['state'] = "<MISSING>"

    #zip
    try:
        k['zip'] = add.split('<br/>')[-1].split(',',1)[1].split(' ')[-1]
    except:
        k['zip'] = "<MISSING>"

    #phone
    try:
        k['phone'] = x.split('loc-result-card-phone-container')[1].split('tel:')[1].split('"')[0]
    except:
        k['phone'] = "<MISSING>"
    #hours
    try:
        k['hours'] = pretty_hours(x.split('mobile-container field-businesshours')[1].split('<table>')[1].split('</table>')[0])
    except:
        k['hours'] = "<MISSING>"

    #type
    k['type'] = "NovaCare" if 'novacare' in x.split('loc-result-card-logo')[1].split('</div>')[0] else "<MISSING>"
    return k

def fetch_data():
    #src="https://resources.selectmedical.com/logos/op/brand-novacare.png"
    #novacare has this above in class=\"loc-result-card-logo\">
    logzilla = sglog.SgLogSetup().get_logger(logger_name='novacare')
    url = 'https://www.novacare.com//sxa/search/results/?s=&itemid={891FD4CE-DCBE-4AA5-8A9C-539DF5FCDE97}&sig=&autoFireSearch=true&v=%7B80D13F78-0C6F-42A0-A462-291DD2D8FA17%7D&p=3000&g=&o=Distance%2CAscending&e=0'
    #API call looks scary but on further inspection didn't see any random tokens/auth/security
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

    session = SgRequests()
    logzilla.info(f'Making API request.. this may take up to one minute')
    son = session.get(url, headers = headers).json()
    logzilla.info(f'Finished request')
    for i in son['Results']:
        store = {}
        store['dic']=i
        store['parsed']=parse_html(i['Html'])
        yield store
    logzilla.info(f'Finished Grabbing data!')
    
         
def scrape():
    url="https://novacare.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url+'/'),
        page_url=MappingField(mapping=['dic','Url'], value_transform = lambda x : url+x),
        location_name=MappingField(mapping=['parsed','name']),
        latitude=MappingField(mapping=['dic','Geospatial','Latitude'], value_transform = lambda x : "<MISSING>" if x == '0' or x == '0.0' else x),
        longitude=MappingField(mapping=['dic','Geospatial','Longitude'], value_transform = lambda x : "<MISSING>" if x == '0' or x == '0.0' else x),
        street_address=MappingField(mapping=['parsed','address'], part_of_record_identity = True),
        city=MappingField(mapping=['parsed','city']),
        state=MappingField(mapping=['parsed','state']),
        zipcode=MappingField(mapping=['parsed','zip']),
        country_code=MissingField(),
        phone=MappingField(mapping=['parsed','phone']),
        store_number=MappingField(mapping=['dic','Id']),
        hours_of_operation=MappingField(mapping=['parsed','hours']),
        location_type=MappingField(mapping=['parsed','type'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='novacare.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
