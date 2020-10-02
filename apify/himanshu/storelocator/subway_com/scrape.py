import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from tenacity import retry, stop_after_attempt
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
}
@retry(stop=stop_after_attempt(7))
def get_data(url):
    session = SgRequests()
    r = session.get(url, headers=headers)
    json_data = json.loads(r.text[1:-1])
    return json_data
def fetch_data():
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    adressess = []
    keys = set()
    search = sgzip.ClosestNSearch()
    search.initialize()
    coord = search.next_coord()
    while coord:
        x = coord[0]
        y = coord[1]
        try:
            json_data = get_data("https://locator-svc.subway.com/v3/GetLocations.ashx?q=%7B%22InputText%22%3A%22%22%2C%22GeoCode%22%3A%7B%22Latitude%22%3A" + str(x) + "%2C%22Longitude%22%3A" + str(y) + "%2C%22CountryCode%22%3A%22US%22%7D%2C%22DetectedLocation%22%3A%7B%22Latitude%22%3A0%2C%22Longitude%22%3A0%2C%22Accuracy%22%3A0%7D%2C%22Paging%22%3A%7B%22StartIndex%22%3A1%2C%22PageSize%22%3A50%7D%2C%22ConsumerParameters%22%3A%7B%22metric%22%3Afalse%2C%22culture%22%3A%22en-US%22%2C%22country%22%3A%22US%22%2C%22size%22%3A%22D%22%2C%22template%22%3A%22%22%2C%22rtl%22%3Afalse%2C%22clientId%22%3A%2217%22%2C%22key%22%3A%22SUBWAY_PROD%22%7D%2C%22Filters%22%3A%5B%5D%2C%22LocationType%22%3A1%2C%22behavior%22%3A%22%22%2C%22FavoriteStores%22%3Anull%2C%22RecentStores%22%3Anull%7D")
        except:
            pass
        location_list = json_data["ResultData"]
        html = json_data["ResultHtml"][2:]
        for store_data in location_list:
            lat = store_data["Geo"]["Latitude"]
            lng = store_data["Geo"]["Longitude"]
            address = store_data["Address"]
            key = json.dumps(address)
            if key in keys:
                keys.add(key)
                continue
            if address["CountryCode"] not in ("US","CA"):
                continue
            store = []
            store.append("https://www.subway.com")
            store.append("<MISSING>")
            street_address = address["Address1"]
            if address["Address2"]:
                street_address = street_address + " " + address["Address2"]
            if address["Address3"]:
                street_address = street_address + " " + address["Address3"]
            store.append(street_address)
            store.append(address["City"] if address["City"] else "<MISSING>")
            store.append(address["StateProvCode"]  if address["StateProvCode"] else "<MISSING>")
            store.append(address["PostalCode"] if address["PostalCode"] else "<MISSING>")
            store.append(address["CountryCode"])
            if store[-1] == "CA":
                store[-2] = store[-2].replace(" ","")
                store[-2] = store[-2][:3] + " " + store[-2][3:]
            try:
                store.append(str(store_data['LocationId']['StoreNumber']))
            except:
                store.append("<MISSING>")
            location_soup =  BeautifulSoup(html[0],"lxml")
            if location_soup.find("div",{'class':"locationOpen"}) == False:
                continue
            try:
                hours = " ".join(list(location_soup.find("div",{'class':'hoursTable'}).stripped_strings))
                phone = location_soup.find("div",{"class":"locatorPhone"}).text.strip()
            except:
                session = SgRequests()
                link_data = "https://order.subway.com/RemoteOrder/Restaurant/RestaurantDetailsAsync"
                payload = "StoreId="+str(store_data['LocationId']['StoreNumber'])
                headers = {
                    'accept': "text/html, */*; q=0.01",
                    'accept-encoding': "gzip, deflate, br",
                    'accept-language': "en-US,en;q=0.9",
                    'content-type': "application/x-www-form-urlencoded",
                    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
                    'x-requested-with': "XMLHttpRequest",
                    'cache-control': "no-cache",
                    'postman-token': "14df7998-ed30-a94b-9293-1f79e93a1493"
                    }
                hour_r = session.post(link_data,data=payload,headers=headers)
                hour_soup = BeautifulSoup(hour_r.text,"lxml")
                hour_data = hour_soup.find("table").find_all("td")
                hoo = []
                for h in hour_data:
                    hoo.append(h.text)
                hours = " ".join(hoo)
                phone = "<MISSING>"
            del html[0]
            if len(phone.replace("-","").replace(" ",""))== 12:
                session = SgRequests()
                link_data = "https://order.subway.com/RemoteOrder/Restaurant/RestaurantDetailsAsync"
                payload = "StoreId="+str(store_data['LocationId']['StoreNumber'])
                headers = {
                    'accept': "text/html, */*; q=0.01",
                    'accept-encoding': "gzip, deflate, br",
                    'accept-language': "en-US,en;q=0.9",
                    'content-type': "application/x-www-form-urlencoded",
                    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
                    'x-requested-with': "XMLHttpRequest",
                    'cache-control': "no-cache",
                    'postman-token': "14df7998-ed30-a94b-9293-1f79e93a1493"
                    }
                phone_r = session.post(link_data,data=payload,headers=headers)
                phone_soup = BeautifulSoup(phone_r.text,"lxml")
                phone = phone_soup.find("div",{"class":"restaurant-phone"}).text.replace("\n","").replace("\r","").strip()
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours if hours else "<MISSING>")
            if hours.count("- - -") >5:
                continue
            store.append("https://order.subway.com/en-US/restaurant/"+str(store_data['LocationId']['StoreNumber']))
            if store[2] in adressess:
                continue
            adressess.append(store[2])
            yield store
        if len(location_list) == MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
