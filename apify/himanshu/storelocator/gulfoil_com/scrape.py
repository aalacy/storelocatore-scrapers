import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    base_url = "http://gulfoil.com"

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    while zip_code:
        location_name = ""
        street_address1 = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = ''
        #print(zip_code)
        result_coords = []
        # q = 0

        data="field_geofield_distance%5Bdistance%5D=500&field_geofield_distance%5Bunit%5D=3959&field_geofield_distance%5Borigin%5D="+str(zip_code)+"&view_name=station_locator_block&view_display_id=block&view_args=&view_path=node%2F21&view_base_path=&view_dom_id=999559f25a324da30a53db55ca017515&pager_element=0&ajax_html_ids%5B%5D=custom-bootstrap-menu&ajax_html_ids%5B%5D=block-views-station-locator-block-block&ajax_html_ids%5B%5D=views-exposed-form-station-locator-block-block&ajax_html_ids%5B%5D=edit-field-geofield-distance-wrapper&ajax_html_ids%5B%5D=edit-field-geofield-distance&ajax_html_ids%5B%5D=edit-field-geofield-distance-distance&ajax_html_ids%5B%5D=edit-field-geofield-distance-unit&ajax_html_ids%5B%5D=edit-field-geofield-distance-origin&ajax_html_ids%5B%5D=edit-submit-station-locator-block&ajax_html_ids%5B%5D=&ajax_html_ids%5B%5D=&ajax_html_ids%5B%5D=mm_sync_back_ground&ajax_page_state%5Btheme%5D=bootstrap_subtheme&ajax_page_state%5Btheme_token%5D=VK5PQBNQBSjygw9s9M9JrEaD1NW8gEEQvtSNaB68auA&ajax_page_state%5Bcss%5D%5Bmodules%2Fsystem%2Fsystem.base.css%5D=1&ajax_page_state%5Bcss%5D%5Bmodules%2Ffield%2Ftheme%2Ffield.css%5D=1&ajax_page_state%5Bcss%5D%5Bmodules%2Fnode%2Fnode.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fviews%2Fcss%2Fviews.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fckeditor%2Fcss%2Fckeditor.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fctools%2Fcss%2Fctools.css%5D=1&ajax_page_state%5Bcss%5D%5Bmodules%2Fgeofield%2Fcss%2Fproximity-element.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fwebform%2Fcss%2Fwebform.css%5D=1&ajax_page_state%5Bcss%5D%5B%2F%2Fcdn.jsdelivr.net%2Fbootstrap%2F3.3.7%2Fcss%2Fbootstrap.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fcss%2F3.3.7%2Foverrides.min.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap_subtheme%2Fcss%2Fstyle.css%5D=1&ajax_page_state%5Bjs%5D%5B0%5D=1&ajax_page_state%5Bjs%5D%5B1%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fjs%2Fbootstrap.js%5D=1&ajax_page_state%5Bjs%5D%5B%2F%2Fajax.googleapis.com%2Fajax%2Flibs%2Fjquery%2F1.10.2%2Fjquery.min.js%5D=1&ajax_page_state%5Bjs%5D%5Bmisc%2Fjquery.once.js%5D=1&ajax_page_state%5Bjs%5D%5Bmisc%2Fdrupal.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fjquery_update%2Freplace%2Fui%2Fexternal%2Fjquery.cookie.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fjquery_update%2Freplace%2Fmisc%2Fjquery.form.min.js%5D=1&ajax_page_state%5Bjs%5D%5Bmisc%2Fajax.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fjquery_update%2Fjs%2Fjquery_update.js%5D=1&ajax_page_state%5Bjs%5D%5B%2F%2Fcdn.jsdelivr.net%2Fbootstrap%2F3.3.7%2Fjs%2Fbootstrap.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fviews%2Fjs%2Fbase.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fjs%2Fmisc%2F_progress.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fwebform%2Fjs%2Fwebform.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fviews%2Fjs%2Fajax_view.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fgoogle_analytics%2Fgoogleanalytics.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fjs%2Fmodules%2Fviews%2Fjs%2Fajax_view.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fjs%2Fmisc%2Fajax.js%5D=1&ajax_page_state%5Bjquery_version%5D=1.10"
        json_data = requests.post("http://gulfoil.com/views/ajax" ,data=data, headers=headers).json()
        for loc in json_data:
            if "data" in loc:
                soup = BeautifulSoup(loc['data'], "lxml")
                table1 = soup.find('table',{'class':'table'})
                table = soup.find_all('table',{'class':'table'})
                current_results_len = len(table)
                for i in range(len(table)):
                    location_name  = table[i].find("span").text
                    address_tage = table[i].find("p")
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(table[i]))
                    if phone_list:
                        phone = phone_list[-1]
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address_tage.text))
                    if us_zip_list:
                        zipp = us_zip_list[-1]
                        country_code = "US"
                    state_list = re.findall(r' ([A-Z]{2})', str(address_tage.text))
                    if state_list:
                        state = state_list[-1]
                    full_address = list(address_tage.stripped_strings)
                    indices = [i for i, s in enumerate(full_address) if zipp in s]
                    city = full_address[indices[0]].replace(state,"").replace(zipp,"").replace(",",'').strip()
                    if indices and indices[0]>0:
                        street_address = " ".join(full_address[:indices[0]])
                    else:
                        street_address = "<MISSING>"
        
                    # print("==========================full_address=  ",full_address)
                    # print("==========================city=  ",city)
                    # print(indices[0],"==========================street_address=  ",street_address)
                    store = []
                    locator_domain =base_url
                    result_coords.append((latitude, longitude))
                    store.append(locator_domain if locator_domain else '<MISSING>')
                    store.append(location_name if location_name else '<MISSING>')
                    store.append(street_address if street_address else '<MISSING>')
                    store.append(city if city else '<MISSING>')
                    store.append(state if state else '<MISSING>')
                    store.append(zipp if zipp else '<MISSING>')
                    store.append(country_code if country_code else '<MISSING>')
                    store.append(store_number if store_number else '<MISSING>')
                    store.append(phone if phone else '<MISSING>')
                    store.append(location_type if location_type else '<MISSING>')
                    store.append(latitude if latitude else '<MISSING>')
                    store.append(longitude if longitude else '<MISSING>')
                    store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                    store.append("<MISSING>")
                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                   # print('---store--'+str(store))
                    yield store
                
            # q= q+1
        if current_results_len < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()           
        # print("===========================================", q)
            

def scrape():
    data = fetch_data()

    write_output(data)


scrape()
