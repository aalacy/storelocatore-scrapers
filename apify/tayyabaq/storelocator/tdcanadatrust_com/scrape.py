import csv
import re
import requests

urls = [
    'https://www.tdbank.com/net/get12.ashx?longitude=-127.64762050000002&latitude=53.7266683&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-116.5765035&latitude=53.9332706&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-98.81387619999998&latitude=53.7608608&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-66.4619164&latitude=46.56531629999999&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-57.66043639999998&latitude=53.1355091&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-63.74431100000004&latitude=44.68198659999999&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-85.32321400000001&latitude=51.25377499999999&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-63.416813599999955&latitude=46.510712&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-71.2079809&latitude=46.8138783&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-106.4508639&latitude=52.9399159&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100',
    'https://www.tdbank.com/net/get12.ashx?longitude=-135&latitude=64.2823274&country=CA&locationtypes=3&json=y&searchradius=500&searchunit=km&numresults=100'
]

def write_output(data):
    with open('tdbank.csv', mode='w',newline='') as output_file:
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
            cont = response.json() #json.loads(html.content)
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
                hoo = i.get('hours', "<MISSING>")
                if len(hoo) < 3:
                    hoo = "<MISSING>"
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
                    city = i['address'].split(',')[1].strip()
                except Exception as e:
                    city = "<MISSING>"
                try:
                    state = i['address'].split(',')[2].strip().replace("PQ", "QC")

                except Exception as e:
                    state = "<MISSING>"
                try:
                    zp = i['address'].split(',')[-1].strip().replace("V7X1KB", "V7X1L4")
                except Exception as e:
                    zp = "<MISSING>"
                page_url = j
                location_name = "TD Canada Trust"
                country_code = "CA"
                locator_domain = "https://www.td.com"
                store_numbr = "<MISSING>"
                new = [locator_domain, page_url,location_name, street, city, state, zp, country_code,store_numbr, phn,
                     loc_type, lat, lng, hoo]
                data_list.append(new)
        print(data_list)
        return data_list

    except Exception as e:
        print(str(e))


def scrape():
    data=fetch_data()
    write_output(data)


scrape()
