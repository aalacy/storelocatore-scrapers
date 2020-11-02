import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # return 2D array to be written to csv
    return_main_object = []
    locator_domain = 'https://kellyexpressmart.com/' 
    ext = 'our-locations/'

    headers = {'User-Agent': 
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

    to_scrape = locator_domain + ext
    page = session.get(to_scrape, headers = headers)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    stores = soup.find_all('div', {'class': 'wpb_column vc_column_container vc_col-sm-4'})
    all_store_data = []

    for store in stores[3:]:

        text = store.text.strip()
        
        split_info = text.splitlines()
        location_name = split_info[1]
        street_address = split_info[1]

        to_split_more = split_info[2].replace('\xa0', '')
        
        split_arr = to_split_more.split(',')
        city = split_arr[0]
        split_arr2 = split_arr[1].split(' ')
        state = split_arr2[1]
        zip_code = split_arr2[2]
        ## no phonenumber
        if len(split_info) == 3:
            phone_number = '<MISSING>'
            
        ## regular case
        if len(split_info) == 4:
            phone_number = split_info[3]
            
        ## either menu option or a random \n    
        if len(split_info) == 5:
            if split_info[3] == '':
                phone_number = split_info[4]
            else:
                phone_number = split_info[3]
                
        ## two empty strings    
        if len(split_info) == 6:
            phone_number = split_info[5]
            
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

        # add geo points
        geo = soup.find_all('div', {'class': 'lmm-geo-tags geo'})
        for g in geo:
            for data in all_store_data:
                if g.text[:5] in data[2]:
                    data[10] = g.find('span',{'class': 'latitude'}).text
                    data[11] = g.find('span',{'class': 'longitude'}).text
                    continue
                    
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
