import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import xmltodict
session = SgRequests()
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Referer": "https://www.gowireless.com/stores",
        "X-Requested-With": "XMLHttpRequest",
    }
    base_url= "https://www.gowireless.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang="
    data = session.get(base_url,headers=headers)
    o = xmltodict.parse(data.text)
    data_json_new = json.loads(json.dumps(o))
    data_tt = data_json_new['locator']['store']
    return_main_object=[]
    for loc in data_tt['item']:
        # print(loc['address'].split("  ")[-1])
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(loc['address'].split("  ")[-1]))
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(loc['address'].split("  ")[-1]))
        state_list = re.findall(r'([A-Z]{2})', str(loc['address'].split("  ")[-1]))
        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"
        state = ''
        #&nbsp; 
        if state_list:
            state = state_list[-1]
        st = loc['address'].split("  ")[0]
        city = loc['address'].split("  ")[1].replace(",",'')
        latitude = loc['latitude']
        longitude = loc['longitude']
        page_url = loc['exturl']
        hours = loc['operatingHours']
        if hours != None:
            hours_of_operation =hours.replace('<span style="color: rgb(85&#44; 85&#44; 85); font-size: 12px;">','').replace("</span>",'').replace('<span style="font-size: 11pt; font-family: Calibri&#44; sans-serif;">','').replace("<p>",'').replace("</p>",'').replace("&nbsp;",'').replace("<br>",'').strip().lstrip()
        # hours = BeautifulSoup(loc['operatingHours'],"lxml").text.replace("&nbsp;",'').replace("<br>",'').strip().lstrip()
        # print(hours.text)
        phone = loc['telephone']
        store_no = loc['storeId']
        tem_var =[]
        tem_var.append("https://www.gowireless.com/")
        tem_var.append(loc['location'])
        tem_var.append(st.replace("&#44;",''))
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipp)
        tem_var.append("US")
        tem_var.append(store_no)
        tem_var.append(phone.replace("96797","<MISSING>"))
        tem_var.append("GoWireless")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(hours_of_operation if hours_of_operation else "<MISSING>")
        tem_var.append(page_url)
        # print(tem_var)
        return_main_object.append(tem_var)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()


