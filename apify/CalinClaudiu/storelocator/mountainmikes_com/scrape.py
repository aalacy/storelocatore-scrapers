from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.simple_scraper_pipeline import *

session = SgRequests()
                                       
def fetch_deeper(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    x=["<MISSING>", "<MISSING>", "<MISSING>", "<MISSING>"] #street_address||city||zipcode||HOO
    x[0]= soup.find_all('a',class_="link_style")[3].get_text()#(has_attrs)
    x[1]=x[0].rsplit(',')[0].split('\n')[-1].lstrip().rstrip()
    x[2]=x[0].split(',')[-1].split('\n')[-2].lstrip().rstrip()
    x[0]=x[0].split(',')[0].split('\n')[1].lstrip().rstrip()
    if '   ' in x[0]:
        x[0]=x[0].split('   ')[0]+' '+x[0].rsplit('   ')[-1]
    x[3]= soup.find('div', class_="store_hours").get_text().split('Hours')[-1].lstrip().rstrip().replace('\n\n\n',';').replace('\n',' ')
    return x

def fetch_data():
    stores={
        'locator_domain' : [],
        'page_url' : [],
        'location_name' : [],
        'latitude' : [],
        'longitude' : [],
        'street_address' : [],
        'city' : [],
        'state' : [],
        'zipcode' : [],
        'country_code' : [],
        'phone' : [],
        'store_number' : [],
        'hours_of_operation' : [],
        'location_type' : [],
        }
    
    url="https://www.mountainmikespizza.com/locations/"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
    
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    states = soup.find_all('div', class_="state_block")
    for state in states:       
        atag = state.find_all('div', class_=lambda value: value and value.startswith("location_block store"))
        for tag in atag:
            if tag.has_attr('data-lat'):
                #stores['locator_domain'].append(url)
                now=tag.find('a', class_="cta link_style cta_angle_rt cta_hover pine_bkd")['href']
                stores['page_url']=now#.append(now)
                stores['location_name']=tag.find('a', class_="cta link_style cta_angle_rt cta_hover pine_bkd").get_text().split("for")[1].lstrip().rstrip()#.append(tag.find('a', class_="cta link_style cta_angle_rt cta_hover pine_bkd").get_text().split("for")[1].lstrip().rstrip())
                stores['phone']=tag.find('a', href=lambda href: href and "tel:" in href).get_text()#.append(tag.find('a', href=lambda href: href and "tel:" in href))
                stores['latitude']=tag['data-lat']#.append(tag['data-lat'])
                stores['longitude']=tag['data-long']#.append(tag['data-long'])
                stores['store_number']=tag['class'][1].rsplit('_')[1]#.append(tag['class'][1].rsplit('_')[1])
                stores['state']=state['id']#.append(state['id'])
                stores['country_code']="US"#.append("US")
                if not tag.find('div', class_="store_status"):
                    stores['location_type']="<MISSING>"#.append("<MISSING>")
                    r2=fetch_deeper(now)
                    stores['street_address']=r2[0]#.append(r2[0])
                    #street address
                    stores['city']=r2[1]#.append(r2[1])
                    #city
                    stores['zipcode']=r2[2]#.append(r2[2])
                    #zipcode
                    stores['hours_of_operation']=r2[3]#.append(r2[3])
                    #HOO
                else:
                    stores['location_type']=tag.find('div', class_="store_status").get_text().lstrip().rstrip()#.append(tag.find('div', class_="store_status").get_text().lstrip().rstrip())

                yield stores
    #return stores


def scrape():
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain= ConstantField("https://www.mountainmikespizza.com/"),
        page_url=MappingField(mapping=['page_url']),
        location_name=MappingField(['location_name']),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MappingField(mapping=['street_address']),
        city=MappingField(['city']),
        state=MappingField(['state']),
        zipcode=MappingField(['zipcode']),
        country_code=ConstantField("US"),
        phone=MappingField(['phone']),
        store_number=MappingField(['store_number']),
        hours_of_operation=MappingField(['hours_of_operation']),
        location_type=MappingField(['location_type'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='mountainmikespizza.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5,
                                     post_process_filter=lambda rec: rec['location_type'] != 'Coming Soon!')

    pipeline.run()

if __name__ == "__main__":
    scrape()

