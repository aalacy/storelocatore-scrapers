import csv
import urllib2
from sgrequests import SgRequests
import sgzip
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    for coord in sgzip.coords_for_radius(50):
        x = float(coord[0])
        y = float(coord[1])
        nelat = x + 2
        swlat = x - 2
        nelng = y + 2
        swlng = y - 2
        url = 'https://www.coffeebean.com/views/ajax?_wrapper_format=drupal_ajax'
        payload = {'field_geo_location_boundary[lat_north_east]': nelat,
                   'field_geo_location_boundary[lng_north_east]': nelng,
                   'field_geo_location_boundary[lat_south_west]': swlat,
                   'field_geo_location_boundary[lng_south_west]': swlng,
                   'field_country_value': '',
                   'field_street_address_value': '',
                   'field_city_value': '',
                   'field_postal_code_value': '',
                   'view_name': 'store_locator',
                   'view_display_id': 'page_1',
                   'view_args': '',
                   'view_path': '/store-locator',
                   'view_base_path': 'store-locator',
                   'view_dom_id': 'efd96bc2aa1efec26195acc5318f674ef3a87ffe91de1109078d4caa28d4c7d8',
                   'pager_element': '0',
                   '_drupal_ajax': '1',
                   'ajax_page_state[theme]': 'cbtl_blend',
                   'ajax_page_state[theme_token]': '',
                   'ajax_page_state[libraries]': 'addtoany/addtoany,cbtl_blend/global-styling,classy/base,classy/messages,classy/node,core/html5shiv,core/normalize,geolocation/geolocation.commonmap,magento_2_api/add-to-cart,paragraphs/drupal.paragraphs.unpublished,system/base,views/views.ajax,views/views.module'
                   }
        r = session.post(url, headers=headers, data=payload)
        for line in r.iter_lines():
            if 'www.coffeebean.com\\/store\\/usa\\/' in line:
                items = line.split('href=\\u0022https:\\/\\/www.coffeebean.com\\/store\\/usa\\/')
                for item in items:
                    if '"command":"' not in item:
                        lurl = item.split('\\u')[0].replace('\\','')
                        lurl = 'https://www.coffeebean.com/store/usa/' + lurl
                        if lurl not in locs:
                            locs.append(lurl)
                            print('%s Locations Found...' % str(len(locs)))
    for coord in sgzip.coords_for_radius(75):
        x = float(coord[0])
        y = float(coord[1])
        nelat = x + 2
        swlat = x - 2
        nelng = y + 2
        swlng = y - 2
        url = 'https://www.coffeebean.com/views/ajax?_wrapper_format=drupal_ajax'
        payload = {'field_geo_location_boundary[lat_north_east]': nelat,
                   'field_geo_location_boundary[lng_north_east]': nelng,
                   'field_geo_location_boundary[lat_south_west]': swlat,
                   'field_geo_location_boundary[lng_south_west]': swlng,
                   'field_country_value': '',
                   'field_street_address_value': '',
                   'field_city_value': '',
                   'field_postal_code_value': '',
                   'view_name': 'store_locator',
                   'view_display_id': 'page_1',
                   'view_args': '',
                   'view_path': '/store-locator',
                   'view_base_path': 'store-locator',
                   'view_dom_id': 'efd96bc2aa1efec26195acc5318f674ef3a87ffe91de1109078d4caa28d4c7d8',
                   'pager_element': '0',
                   '_drupal_ajax': '1',
                   'ajax_page_state[theme]': 'cbtl_blend',
                   'ajax_page_state[theme_token]': '',
                   'ajax_page_state[libraries]': 'addtoany/addtoany,cbtl_blend/global-styling,classy/base,classy/messages,classy/node,core/html5shiv,core/normalize,geolocation/geolocation.commonmap,magento_2_api/add-to-cart,paragraphs/drupal.paragraphs.unpublished,system/base,views/views.ajax,views/views.module'
                   }
        r = session.post(url, headers=headers, data=payload)
        for line in r.iter_lines():
            if 'www.coffeebean.com\\/store\\/usa\\/' in line:
                items = line.split('href=\\u0022https:\\/\\/www.coffeebean.com\\/store\\/usa\\/')
                for item in items:
                    if '"command":"' not in item:
                        lurl = item.split('\\u')[0].replace('\\','')
                        lurl = 'https://www.coffeebean.com/store/usa/' + lurl
                        if lurl not in locs:
                            locs.append(lurl)
                            print('%s Locations Found...' % str(len(locs)))
    for coord in sgzip.coords_for_radius(100):
        x = float(coord[0])
        y = float(coord[1])
        nelat = x + 2
        swlat = x - 2
        nelng = y + 2
        swlng = y - 2
        url = 'https://www.coffeebean.com/views/ajax?_wrapper_format=drupal_ajax'
        payload = {'field_geo_location_boundary[lat_north_east]': nelat,
                   'field_geo_location_boundary[lng_north_east]': nelng,
                   'field_geo_location_boundary[lat_south_west]': swlat,
                   'field_geo_location_boundary[lng_south_west]': swlng,
                   'field_country_value': '',
                   'field_street_address_value': '',
                   'field_city_value': '',
                   'field_postal_code_value': '',
                   'view_name': 'store_locator',
                   'view_display_id': 'page_1',
                   'view_args': '',
                   'view_path': '/store-locator',
                   'view_base_path': 'store-locator',
                   'view_dom_id': 'efd96bc2aa1efec26195acc5318f674ef3a87ffe91de1109078d4caa28d4c7d8',
                   'pager_element': '0',
                   '_drupal_ajax': '1',
                   'ajax_page_state[theme]': 'cbtl_blend',
                   'ajax_page_state[theme_token]': '',
                   'ajax_page_state[libraries]': 'addtoany/addtoany,cbtl_blend/global-styling,classy/base,classy/messages,classy/node,core/html5shiv,core/normalize,geolocation/geolocation.commonmap,magento_2_api/add-to-cart,paragraphs/drupal.paragraphs.unpublished,system/base,views/views.ajax,views/views.module'
                   }
        r = session.post(url, headers=headers, data=payload)
        for line in r.iter_lines():
            if 'www.coffeebean.com\\/store\\/usa\\/' in line:
                items = line.split('href=\\u0022https:\\/\\/www.coffeebean.com\\/store\\/usa\\/')
                for item in items:
                    if '"command":"' not in item:
                        lurl = item.split('\\u')[0].replace('\\','')
                        lurl = 'https://www.coffeebean.com/store/usa/' + lurl
                        if lurl not in locs:
                            locs.append(lurl)
                            print('%s Locations Found...' % str(len(locs)))
    for loc in locs:
        r = session.get(loc, headers=headers)
        print('Pulling Location %s...' % loc)
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        typ = '<MISSING>'
        country = 'US'
        store = '<MISSING>'
        phone = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        website = 'coffeebean.com'
        for line in r.iter_lines():
            if '<span class="field-content">' in line:
                name = line.split('<span class="field-content">')[1].split('<')[0]
            if '<span property="streetAddress">' in line:
                add = line.split('<span property="streetAddress">')[1].split('<')[0]
            if '<span property="addressLocality">' in line:
                city = line.split('<span property="addressLocality">')[1].split('<')[0]
            if '<span property="addressRegion">' in line:
                state = line.split('<span property="addressRegion">')[1].split('<')[0]
            if '<span property="postalCode">' in line:
                zc = line.split('<span property="postalCode">')[1].split('<')[0]
            if '<meta property="latitude" content="' in line:
                lat = line.split('<meta property="latitude" content="')[1].split('"')[0]
            if '<meta property="longitude" content="' in line:
                lng = line.split('<meta property="longitude" content="')[1].split('"')[0]
            if 'name-field-weekday' in line:
                day = line.split('">')[1].split('<')[0]
            if 'name-field-store-open' in line:
                hro = line.split('">')[1].split('<')[0]
            if 'name-field-store-closed' in line:
                hrs = day + ': ' + hro + '-' + line.split('">')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
            lng = '<MISSING>'
        if name == '':
            name = city
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
