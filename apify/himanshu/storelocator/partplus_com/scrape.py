import csv 
import http.client
from bs4 import BeautifulSoup
import re
import json 
import requests
from random import choice


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
## using proxy 
def get_proxy():
    url = "https://www.sslproxies.org/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html5lib")
    return {'https': (choice(list(map(lambda x:x[0]+':'+x[1],list(zip(map(lambda x:x.text,soup.findAll('td')[::8]),map(lambda x:x.text,soup.findAll('td')[1::8])))))))}

    
def proxy_request(request_type, url, **kwargs):
    while 1:
        try:
            proxy = get_proxy()
            # print("Using Proxy {}".format(proxy))
            r = requests.request(request_type, url, proxies=proxy, timeout=5, **kwargs)
            break
        except:
            pass
    return r

def fetch_data():
    addressess = []
    base_url = "https://www.partsplus.com/"
    region = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH",'OK',"OR","PA","RI","SC","SD",'TN',"TX","UT","VT","VA","WA","WV","WI","WY"]
    for state_id in region:
        #print(state_id)
        data = {"ScriptManager1": "ScriptManager1|btnFindLocations",
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": "SwhIcMWsGfj6tOOjag6D7Um4a/d0puHU6T61Rlv1TWlzR2/x6GTPc25kANFdvm7WGFTv2cGEMF3/N4BoOj7Dbl/BS6KHQlWrmEqwOuBsDUR1+T51zX4CRsq78A9rN5WNczV3iVko9gRP27QvD9F8DHWPFiWQH4cib/BkR+vaCECG1p/ORxZBNETI+eHWir/U",
                "__VIEWSTATEGENERATOR": "CDF2FC7E",
                "__EVENTVALIDATION": "lL04lwcyXw8cdxFoPb+VjKsvCKic99PVzFshuqbR1hAt8dt1eFoC1zssIPl/Z425xBQHDaioh2EqL7agnuhqwI+SrwU8bKtn8jwn2/GM4tfJpl5LoVx4Es9/l7DbYnweJheKNQN10OfAFc1gHliq02jJQhnMa+ePGsZyRypOhBF9hfb4kBjVHUG1EoCg24WssuCNWgG5qzMmCwqZjNN26dLXAaAGBJaplZt6sMjnhCyjUa31CmMSl6gBrY0bmNRo9XDlCuglTSRtzN+mqIuNClTFX8sdwzGNpcQNglPNznTkDiNToLUK0Ikl9rHimU/eNBGunRaz0bMsFrNd3qWLsw==",
                "ddlLocation": "",
                "txtSearchTerm": str(state_id),
                "ddlMiles": "500",
                "__ASYNCPOST": "true",
                "btnFindLocations": "Find Locations"}
        headers = {
            'Accept': '*/*',
            'Host': 'locator.networkhq.org',
            'Origin': 'https://locator.networkhq.org',
            'Referer': 'https://locator.networkhq.org/LocatorFrame.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36',
            'X-MicrosoftAjax': 'Delta=true',
            'X-Requested-With': 'XMLHttpRequest',
                }
        r = proxy_request("post","https://locator.networkhq.org/LocatorFrame.aspx", data=data, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        latitude = []
        longitude = []
        try:
            json_data = json.loads(re.sub(r"'",'"',soup.text.split("|LoadMap(")[1].split(", 6);|")[0].replace("\t"," ")))
            for data in json_data:
                latitude.append(data['lat'])
                longitude.append(data['lng'])
        except:
            latitude.append("<MISSING>")
            longitude.append("<MISSING>")
        
        for index,info in enumerate(soup.find("table").find_all("tr")[1:]):
            location_name = info.find("span",{"class":"shop"}).text.strip()
            addr = list(info.find("span",{"class":"desc"}).stripped_strings)
            street_address = " ".join(addr[:-1])
            city = addr[-1].split(",")[0]
            state = addr[-1].split(",")[1].split(" ")[1]
            zipp = " ".join(addr[-1].split(",")[1].split(" ")[2:]).strip()
            phone = info.find_all("td")[1].find("a").text.replace("Call:","").replace("\t"," ").strip()
            location_type = re.sub(r'\s+'," ",info.find_all("td")[-1].text.replace("Website","").replace("Directions","")).strip()
            
            if re.sub(r'\s+'," ",info.find_all("td")[-1].find_all("span",{"class":"directions"})[-1].text).strip() == "Website":
                page_url = info.find_all("td")[-1].find_all("span",{"class":"directions"})[-1].find("a")['href']
            else:
                page_url = "<MISSING>"
            
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US" if zipp.replace("-","").isdigit() else "CA")
            store.append("<MISSING>")
            store.append(phone)
            store.append(location_type)
            store.append(latitude[index])
            store.append(longitude[index])
            store.append("<INACCESSIBLE>")
            store.append(page_url)
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            # print(store)
            yield store
    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
