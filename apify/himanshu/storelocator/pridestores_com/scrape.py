import csv
import re
import pdb
import requests
from lxml import etree
import json
from bs4 import BeautifulSoup

base_url = 'https://pridestores.com'




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.pridestores.com//_api/wix-code-public-dispatcher/siteview/wix/data-web.jsw/find.ajax?gridAppId=2bde48e6-6cdf-4b33-94d6-a40bbdd6bb61&instance=wixcode-pub.8151d6a1c1dacc6443831777da81b8e06b8aeeac.eyJpbnN0YW5jZUlkIjoiYTRkMTY0MzctN2FlOC00NjhlLWIyZjEtMjZjOWNhYTM2Yzg0IiwiaHRtbFNpdGVJZCI6IjAzNDgyY2Y0LWQxNTQtNDM4OC1hMDIzLTk0NGYzZjNlOGE3ZSIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTU5MTc2NTc1NzczMywiYWlkIjoiMGI1ZDRmOGYtOTgzYi00ZWQzLTgxMDktM2ZmYzY2ZjM1NzkxIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6ImJmNDc3NDBiLTMwMTAtNGY4Yy05YzI4LWY0NmE4MjYzNjNhYyIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IlNob3dXaXhXaGlsZUxvYWRpbmcsQWRzRnJlZSxIYXNEb21haW4iLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiMzY1ZTJhNjAtOGNlZS00ZDMwLWE0YTYtOWIyNTQ0NDRhYzNmIiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsfQ==&viewMode=site"
    session = requests.Session()
    headers = {
    'accept': '*/*',
    'content-length': '50',
    'origin': 'https://www.pridestores.com',
    'referer': 'https://www.pridestores.com/_partials/wix-bolt/1.6050.0/node_modules/viewer-platform-worker/dist/bolt-worker.js',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    #   'x-xsrf-token': '1591764301|qXg8PlC4AODi',
    'Content-Type': 'application/json'
    }

    request = session.post(url, headers=headers, data="[\"Locations\",null,[{\"city\":\"asc\"}],0,32,null,null]")

    store_list = json.loads(request.text)
    for index,store in enumerate(store_list['result']['items']):
        hours=''
        street_address = store['address']
        # location_name = store['city']+' Pride '
        phone = store['phone']
        hours = store['hours']
        try:
            hours=hours+' '+store['satHours']
        except:
            hours=hours
        state =''
        # print("https://www.pridestores.com"+store['url'])
        page_url = "https://www.pridestores.com"+store['url']
        r = requests.get("https://www.pridestores.com"+store['url'])
        soup = BeautifulSoup(r.text,"html.parser")
        a = soup.find_all("a",{"href":re.compile("https://www.google.com/maps")})
        # if a!=[]:
        #     latitude=soup.find_all("a",{"href":re.compile("https://www.google.com/maps")})[0]['data-content'].split("/@")[1].split(",")[1]
        #     print(soup.find_all("a",{"href":re.compile("https://www.google.com/maps")})[0]['data-content'].split("/@")[1].split(",")[2])
        # print( soup.find_all("div",{"class":"txtNew","data-packed":"true"})[1].text)
        if index==0:
            try:
                location_name = soup.find_all("div",{"class":"txtNew","data-packed":"true"})[1].text
                # print(name)
                full = soup.find("div",{"class":"txtNew","data-packed":"true"}).text
                city = full.split(",")[1]
                state_list = re.findall(r' ([A-Z]{2})', str(full))
                if state_list:
                    state = state_list[-1]
            except:
                pass
        else:
            try:
                location_name = soup.find_all("div",{"class":"txtNew","data-packed":"true"})[0].text
                # print(location_name)
                full = soup.find_all("div",{"class":"txtNew","data-packed":"true"})[1].text
                city = full.split(",")[1]
                state_list = re.findall(r' ([A-Z]{2})', str(full))
                if state_list:
                    state = state_list[-1]
            except:
                pass
        store1=[]
        store1.append("https://www.pridestores.com/")
        store1.append(location_name)
        store1.append(street_address)
        store1.append(city)
        store1.append(state)
        store1.append( "<MISSING>")
        store1.append("US")
        store1.append("<MISSING>")
        store1.append(phone if phone else "<MISSING>")
        store1.append("<MISSING>")
        store1.append("<MISSING>")
        store1.append( "<MISSING>")
        store1.append(hours if hours else "<MISSING>")
        store1.append(page_url)
     
        store1 = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store1]
        # print("----------------------",store1)
        yield store1
        # print("~~~~~~~~~~~~~~~~~~~~~~~")
      

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
