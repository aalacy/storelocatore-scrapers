import csv
import re
import requests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tdcanadatrust_com')



headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

r = requests.get('https://www.tdbank.com/net/get12.ashx?longitude=-79.2998&latitude=85.1076&country=CA&locationtypes=3&json=y&searchradius=4000&searchunit=mi&numresults=1900',headers=headers)      
cont = json.loads(r.content,strict=False)
l = cont['markers']['marker']

y=['https://www.tdbank.com/net/get12.ashx?longitude=-79.2998&latitude=85.1076&country=CA&locationtypes=3&json=y&searchradius=4000&searchunit=mi&numresults=1900']

addresses=[]
data_list=[]

def write_output(data):
    with open('data.csv', mode='w',newline='',encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    try:    
        for i in l:
            if i.get('address') in addresses:
                continue
            addresses.append(i.get('address'))
            lat = i.get('lat', "<MISSING>")
            lng = i.get('lng', "<MISSING>")
            phn = i.get('phoneNo', "<MISSING>")
            if len(phn) < 3:
                phn = "<MISSING>"
            try: 
                new = i['hours']
                if new=={}:
                    new = "<MISSING>"
                    hour=new
                else:
                    hr=[]
                    for key, value in new.items():
                        n = key + " " + value
                        hr.append(n)
                        hour = " ".join(hr)

            except Exception as e:
                hour = "<MISSING>"
                
            try:
                l_type = i['branchtype']
                loc_type = re.sub(r'(((?<=\s)|^|-)[a-z])', lambda x: x.group().upper(), l_type)
                if loc_type == '':
                    loc_type = "ATM"
            except Exception as e:
                loc_type = "<MISSING>"

            try:
                street = i['address'].split(',')[0]
            except Exception as e:
                street = "<MISSING>"

            try:
                city = i['address'].split(',')[-3].strip()
            except Exception as e:
                city = "<MISSING>"

            try:
                state = i['address'].split(',')[-2].strip().replace("PQ", "QC")

            except Exception as e:
                state = "<MISSING>"
            
            try:
                zp =i['address'].split(',')[-1].strip().replace("V7X1KB", "V7X1L4").replace("KOE1T0", "K0E1T0").replace("JOL1NO","J0L1N0")

            except Exception as e:
                zp = "<MISSING>"

            page_url = y[0]
            
            try:
                store_numbr =i['id']
                if store_numbr == '':
                    store_numbr = "<MISSING>"
                else:
                    store_numbr = i['id']

            except Exception as e:
                store_numbr = "<MISSING>"
                
            location_name = "<MISSING>"
            country_code = "CA"
            locator_domain = "https://www.td.com"

            new = [locator_domain, page_url,location_name, street, city, state, zp, country_code,store_numbr, phn,
                 loc_type, lat, lng, hour]
            data_list.append(new)
        return data_list

    except Exception as e:
        logger.info(str(e))

def scrape():
    data=fetch_data()
    write_output(data)

scrape()
