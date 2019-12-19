import csv
import re
import requests
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

r = requests.get('https://www.tdbank.com/net/get11.ashx?longitude=-94.57868&latitude=43.0997&searchradius=9000&searchunit=mi&locationtypes=3&numresults=1300&json=y&country=us',headers=headers)      
cont = json.loads(r.content,strict=False)
l = cont['markers']['marker']

y=['https://www.tdbank.com/net/get11.ashx?longitude=-94.57868&latitude=43.0997&searchradius=9000&searchunit=mi&locationtypes=3&numresults=1300&json=y&country=us']

addresses=[]
data_list=[]

def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
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
            hr=[]
            hoo = i.get('hours', "<MISSING>")
            for key, value in hoo.items():
                n = key + " " + value
                hr.append(n)
                hour = "| ".join(hr)

            if len(hour) < 3:
                hour = "<MISSING>"

            try:
                new = i['address']
                st=new.replace("(", "").replace(")", "")
                street=st.split(',')[0]

            except Exception as e:
                street = "<MISSING>"

            c = i['address']
            try:
                cc = re.findall(r'.*\D+\d{5}', c)
                ct = cc[0].replace(")", "").replace("(", "")
                city=ct.split(',')[-3].strip()

            except Exception as e:
                city = "<MISSING>"

            try:
                s = re.findall(r'.*\D+\d{5}', c)
                st = s[0].replace(")", "").replace("(", "")
                state=st.split(',')[-2].strip()

            except Exception as e:
                state = "<MISSING>"

            try:
                zp = i['address']
                zp_code = re.findall(r"\d{5}", zp)
                zip_code=zp_code[0]

            except Exception as e:
                zip_code = "<MISSING>"

            store_numbr = i.get('branchN', "<MISSING>")
            if len(store_numbr) < 3:
                store_numbr = "<MISSING>"

            page_url = y
            location_name = "TD BANK"
            loc_type = "ATM"
            country_code = "USA"
            locator_domain = "https://www.td.com"

            new = [locator_domain, page_url,location_name, street, city, state, zip_code, country_code,store_numbr, phn,
                 loc_type, lat, lng, hour]
            data_list.append(new)
        return data_list

    except Exception as e:
        print(str(e))

def scrape():
    data=fetch_data()
    write_output(data)


scrape()
