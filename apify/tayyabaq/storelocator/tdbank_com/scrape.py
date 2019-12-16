import csv
import re
import requests
import json

urls=['https://www.tdbank.com/net/get11.ashx?longitude=-72.57784149999998&latitude=44.5588028&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-75.52766989999998&latitude=38.9108325&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-71.57239529999998&latitude=43.1938516&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-69.44546889999998&latitude=45.253783&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-73.08774900000003&latitude=41.6032207&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-80.45490259999997&latitude=38.5976262&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-79.01929969999998&latitude=35.7595731&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-81.1637245&latitude=33.836081&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-77.19452469999999&latitude=41.2033216&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-76.6412712&latitude=39.0457549&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-78.65689420000001&latitude=37.4315734&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-71.4774291&latitude=41.5800945&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-71.38243740000001&latitude=42.4072107&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-77.03687070000001&latitude=38.9071923&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-81.51575350000002&latitude=27.6648274&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
    'https://www.tdbank.com/net/get11.ashx?longitude=-74.0059728&latitude=40.7127753&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=07:56&Json=y&callback=',
     'https://www.tdbank.com/net/get11.ashx?longitude=-74.4056612&latitude=40.0583238&searchradius=200&searchunit=mi&locationtypes=3&numresults=30&time=03:43&Json=y&callback=']

def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        writer.writerows(data)

data_list = []
addresses = []

def fetch_data():
    try:
        for j in urls:
            response = requests.request('GET', j, verify=True)
            cont = response.json(strict=False)
            l = cont.get('markers', {}).get('marker', [])

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
                if "OpenNow" in hoo:
                    del hoo["OpenNow"]
                    for key, value in hoo.items():
                        n=key+ " " + value
                        hr.append(n)
                hour="| ".join(hr)

                if len(hour) < 3:
                    hour = "<MISSING>"
                try:
                    l_type = i['branchtype']
                    loc_type = re.sub(r'(((?<=\s)|^|-)[a-z])', lambda x: x.group().upper(), l_type)
                    if loc_type == '':
                        loc_type = "ATM"
                except Exception as e:
                    loc_type = "<MISSING>"
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

                page_url = j
                location_name = "TD BANK"
                country_code = "CA"
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
