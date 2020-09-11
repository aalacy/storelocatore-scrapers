import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.bikramyoga.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '') + ' '
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.bikramyoga.com/wp-admin/admin-ajax.php"
    page_url = 'https://www.bikramyoga.com/studios/studio-locator'
    session = requests.Session()
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    formdata = {
        'address': '',
        'formdata': 'addressInput=',
        'lat': '37.09024',
        'lng': '-95.71289100000001',
        'name': '',
        'options[bubblelayout]': '''<div id="slp_info_bubble_[slp_location id]" class="slp_info_bubble [slp_location featured]">
            <span id="slp_bubble_name"><strong>[slp_location name  suffix  br]</strong></span>
            <span id="slp_bubble_address">[slp_location address       suffix  br]</span>
            <span id="slp_bubble_address2">[slp_location address2      suffix  br]</span>
            <span id="slp_bubble_city">[slp_location city          suffix  comma]</span>
            <span id="slp_bubble_state">[slp_location state suffix    space]</span>
            <span id="slp_bubble_zip">[slp_location zip suffix  br]</span>
            <span id="slp_bubble_country"><span id="slp_bubble_country">[slp_location country       suffix  br]</span></span>
            <span id="slp_bubble_directions">[html br ifset directions]
            [slp_option label_directions wrap directions]</span>
            <span id="slp_bubble_website">[html br ifset url][slp_location web_link][html br ifset url]</span>
            <span id="slp_bubble_email">[slp_location email         wrap    mailto ][slp_option label_email ifset email][html closing_anchor ifset email][html br ifset email]</span>
            <span id="slp_bubble_phone">[html br ifset phone]
            <span class="location_detail_label">[slp_option   label_phone   ifset   phone]</span>[slp_location phone         suffix    br]</span>
            <span id="slp_bubble_fax"><span class="location_detail_label">[slp_option   label_fax     ifset   fax  ]</span>[slp_location fax           suffix    br]<span>
            <span id="slp_bubble_description"><span id="slp_bubble_description">[html br ifset description]
            [slp_location description raw]</span>[html br ifset description]</span>
            <span id="slp_bubble_hours">[html br ifset hours]
            <span class="location_detail_label">[slp_option   label_hours   ifset   hours]</span>
            <span class="location_detail_hours">[slp_location hours         suffix    br]</span></span>
            <span id="slp_bubble_img">[html br ifset img]
            [slp_location image         wrap    img]</span>
            <span id="slp_tags">[slp_location tags]</span>
            </div>''',
        'options[ignore_radius]': '0',
        'options[map_domain]': 'maps.google.com',
        'options[no_autozoom]': '0',
        'options[no_homeicon_at_start]': '1',
        'options[radius_behavior]': 'always_use',
        'options[results_layout]': '''<div id="slp_results_[slp_location id]" class="results_entry location_primary [slp_location featured]">
                <div class="results_row_left_column"   id="slp_left_cell_[slp_location id]"   >
                    
                    <span class="location_name">[slp_location name] [slp_location uml_buttons] [slp_location gfi_buttons]</span>
                    <span class="location_distance">[slp_location distance format="decimal1"] [slp_option distance_unit]</span>
                    
                </div>
                <div class="results_row_center_column location_secondary" id="slp_center_cell_[slp_location id]" >
                    
                    <span class="slp_result_address slp_result_street">[slp_location address]</span>
                    <span class="slp_result_address slp_result_street2">[slp_location address2]</span>
                    <span class="slp_result_address slp_result_citystatezip">[slp_location city_state_zip]</span>
                    <span class="slp_result_address slp_result_country">[slp_location country]</span>
                    <span class="slp_result_address slp_result_phone">[slp_location phone]</span>
                    <span class="slp_result_address slp_result_fax">[slp_location fax]</span>
                                
                </div>
                <div class="results_row_right_column location_tertiary"  id="slp_right_cell_[slp_location id]"  >
                    
                    <span class="slp_result_contact slp_result_website">[slp_location web_link raw]</span>
                    <span class="slp_result_contact slp_result_email">[slp_location email_link]</span>
                    <span class="slp_result_contact slp_result_directions"><a href="https://[slp_option map_domain]/maps?saddr=[slp_location search_address]&amp;daddr=[slp_location location_address]" target="_blank" class="storelocatorlink">[slp_option label_directions]</a></span>
                    <span class="slp_result_contact slp_result_hours">[slp_location hours format text]</span>
                    [slp_location pro_tags raw]
                    [slp_location iconarray wrap="fullspan"]
                    [slp_location eventiconarray wrap="fullspan"]
                    [slp_location socialiconarray wrap="fullspan"]
                    
                    </div>
            </div>''',
        'options[slplus_version]': '4.6',
        'options[use_sensor]': '0',
        'options[message_no_api_key]': 'This site most likely needs a Google Maps API key.',
        'options[distance_unit]': 'miles',
        'options[radii]': '10,25,50,100,(200),500',
        'options[map_center]': 'United States',
        'options[map_center_lat]': '37.09024',
        'options[map_center_lng]': '-95.712891',
        'options[zoom_level]': '12',
        'options[zoom_tweak]': '0',
        'options[map_type]': 'roadmap',
        'options[map_home_icon]': 'https://www.bikramyoga.com/wp-content/plugins/store-locator-le/images/icons/box_yellow_home.png',
        'options[map_end_icon]': 'https://www.bikramyoga.com/wp-content/plugins/store-locator-le/images/icons/bulb_red.png',
        'options[immediately_show_locations]': '0',
        'options[initial_radius]': '',
        'options[initial_results_returned]': '500',
        'options[message_no_results]': 'No locations found.',
        'options[label_website]': 'Website',
        'options[label_directions]': 'Directions',
        'options[label_email]': 'Email',
        'options[label_phone]': 'Phone ',
        'options[label_fax]': 'Fax',
        'options[layout]': '<div id="sl_div">[slp_search][slp_map][slp_results]</div>',
        'options[maplayout]': '[slp_mapcontent][slp_maptagline]',
        'options[resultslayout]': '''<div id="slp_results_[slp_location id]" class="results_entry location_primary [slp_location featured]">
                <div class="results_row_left_column"   id="slp_left_cell_[slp_location id]"   >
                    [slp_addon section=primary position=first]
                    <span class="location_name">[slp_location name] [slp_location uml_buttons] [slp_location gfi_buttons]</span>
                    <span class="location_distance">[slp_location distance_1] [slp_location distance_unit]</span>
                    [slp_addon section=primary position=last]
                </div>
                <div class="results_row_center_column location_secondary" id="slp_center_cell_[slp_location id]" >
                    [slp_addon section=secondary position=first]
                    <span class="slp_result_address slp_result_street">[slp_location address]</span>
                    <span class="slp_result_address slp_result_street2">[slp_location address2]</span>
                    <span class="slp_result_address slp_result_citystatezip">[slp_location city_state_zip]</span>
                    <span class="slp_result_address slp_result_country">[slp_location country]</span>
                    <span class="slp_result_address slp_result_phone">[slp_location phone]</span>
                    <span class="slp_result_address slp_result_fax">[slp_location fax]</span>
                    [slp_addon section=secondary position=last]            
                </div>
                <div class="results_row_right_column location_tertiary"  id="slp_right_cell_[slp_location id]"  >
                    [slp_addon section=tertiary position=first]
                    <span class="slp_result_contact slp_result_website">[slp_location web_link]</span>
                    <span class="slp_result_contact slp_result_email">[slp_location email_link]</span>
                    <span class="slp_result_contact slp_result_directions"><a href="https://[slp_option map_domain]/maps?saddr=[slp_location search_address]&daddr=[slp_location location_address]" target="_blank" class="storelocatorlink">[slp_location directions_text]</a></span>
                    <span class="slp_result_contact slp_result_hours">[slp_location hours]</span>
                    [slp_location pro_tags]
                    [slp_location iconarray wrap="fullspan"]
                    [slp_location eventiconarray wrap="fullspan"]
                    [slp_location socialiconarray wrap="fullspan"]
                    [slp_addon section=tertiary position=last]
                    </div>
            </div>''',
        'options[searchlayout]': '''<div id="address_search" class="slp search_box">
                [slp_search_element add_on location="very_top"]
                [slp_search_element input_with_label="name"]
                [slp_search_element input_with_label="address"]
                [slp_search_element dropdown_with_label="city"]
                [slp_search_element dropdown_with_label="state"]
                [slp_search_element dropdown_with_label="country"]
                [slp_search_element selector_with_label="tag"]
                [slp_search_element dropdown_with_label="category"]
                [slp_search_element dropdown_with_label="gfl_form_id"]
                [slp_search_element add_on location="before_radius_submit"]
                <div class="search_item">
                    [slp_search_element dropdown_with_label="radius"]
                    [slp_search_element button="submit"]
                </div>
                [slp_search_element add_on location="after_radius_submit"]
                [slp_search_element add_on location="very_bottom"]
            </div>''',
        'options[theme]': '',
        'options[id]': '',
        'options[hide_search_form]': '',
        'options[force_load_js]': '0',
        'options[map_region]': 'us',
        'radius': '',
        'tags': '',
        'action': 'csl_ajax_onload'
    }
    request = session.post(url, headers=headers, data=formdata, verify=False)
    store_list = json.loads(request.text)['response']
    for store in store_list:
        country = validate(store['country'])
        if country == 'United States' or country == 'Canada':
            output = []
            output.append(base_url) # url
            output.append(get_value(store['url'])) # page url
            output.append(get_value(store['name'])) #location name
            output.append(get_value(store['address'])) #address
            output.append(get_value(store['city'])) #city
            output.append(get_value(store['state'])) #state
            output.append(get_value(store['zip'])) #zipcode
            output.append(country) #country code
            output.append(get_value(store['id'])) #store_number
            output.append(get_value(store['phone'])) #phone
            output.append('Bikram Yoga') #location type
            output.append(get_value(store['lat'])) #latitude
            output.append(get_value(store['lng'])) #longitude
            store_hours = []
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
