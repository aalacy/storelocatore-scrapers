import csv
import re
import pdb
import requests
from lxml import etree
import json
from bs4 import BeautifulSoup as bs

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
    dics={}
    ldata = bs(session.get("https://www.pridestores.com/wl").text,'lxml')
    lats = ldata.find(lambda tag: (tag.name == "script" or tag.name == "h2") and "var serviceTopology" in tag.text.strip()).text.split("var publicModel =")[1].split("var googleAnalytics")[0].replace('"};','"}')
    for q in json.loads(lats)['htmlEmbeds']:
        # print(len( json.loads(q['content']['html'].replace("</script>",'').replace("<script type='application/ld+json'>",''))['hasMap']))
        for gmap in json.loads(q['content']['html'].replace("</script>",'').replace("<script type='application/ld+json'>",''))['hasMap']:
            
            lat = gmap.split("/@")[1].split(',')[0]
            log = gmap.split("/@")[1].split(',')[1]
            dics[gmap.split("place/")[-1].split(',')[0].replace("+",' ').lower()] = {"lat":lat,"log":log}
    # print(dics)

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
        soup = bs(r.text,"html.parser")

        # lats = soup.find(lambda tag: (tag.name == "script" or tag.name == "h2") and "var serviceTopology" in tag.text.strip()).text.split("var publicModel =")[1].split("var googleAnalytics")[0].replace('"};','"}')
        # for q in json.loads(lats)['htmlEmbeds']:
        #     for gmap in json.loads(q['content']['html'].replace("</script>",'').replace("<script type='application/ld+json'>",''))['hasMap']:
        #         lat = gmap.split("/@")[1].split(',')[0]
        #         log = gmap.split("/@")[1].split(',')[1]
        #         print(gmap.split("place/")[-1].split(',')[0].replace("+",' '))

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
        # print(street_address.lower())
        if street_address.lower().replace("n.",'n').replace("234 east main st",'234 e main st') in dics:
            # print( dics[street_address.lower().replace("n.",'n') ])
            latitude = dics[street_address.lower().replace("n.",'n').replace("234 east main st",'234 e main st') ]['lat']
            longitude = dics[street_address.lower().replace("n.",'n').replace("234 east main st",'234 e main st') ]['log']
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        store1.append(street_address)
        store1.append(city)
        store1.append(state)
        store1.append( "<MISSING>")
        store1.append("US")
        store1.append("<MISSING>")
        store1.append(phone if phone else "<MISSING>")
        store1.append("<MISSING>")
        store1.append(latitude)
        store1.append(longitude)
        store1.append(hours if hours else "<MISSING>")
        # if 
        store1.append(page_url.lower())
     
        store1 = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store1]
        # print("----------------------",store1)
        yield store1
        # print("~~~~~~~~~~~~~~~~~~~~~~~")
      

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
