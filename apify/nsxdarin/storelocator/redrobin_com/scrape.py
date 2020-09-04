import csv
import urllib.request, urllib.error, urllib.parse
import requests
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.redrobin.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://redrobin.com/locations/' in line:
            items = line.split('<loc>https://redrobin.com/locations/')
            for item in items:
                if '</loc>' in item:
                    lurl = 'https://redrobin.com/locations/' + item.split('<')[0]
                    if lurl.count('/') == 4 and lurl != 'https://redrobin.com/locations/':
                        locs.append(lurl)
    for loc in locs:
        headers2 = {'content-type': 'application/json',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                    'x-api-key': 'Dx3zjnmVaT2Rvhbs8cwLB8ER0SvwaxmZ1cwSmZ4e',
                    'origin': 'https://www.redrobin.com',
                    'authorization': 'none',
                    'group-member-id': 'none',
                    'authority': 'api.burgerblaster.io',
                    'referer': 'https://www.redrobin.com/locations/sunset-galleria/'
                    }
        slug = loc.rsplit('/',1)[1]
        print(('Pulling Location %s...' % slug))
        website = 'redrobin.com'
        typ = 'Restaurant'
        hours = ''
        payload = '{"operationName":"RestaurantBySlugQuery","variables":{"restaurantSlug":"' + slug + '"},"query":"query RestaurantBySlugQuery($restaurantSlug: String!) {  restaurants {    byRestaurantSlug(slug: $restaurantSlug) {      ...RestaurantDetails      __typename    }    __typename  }}fragment RestaurantDetails on RestaurantInfo {  address {    ...Address    __typename  }  bannerImage {    ...BannerImage    __typename  }  gallery {    ...GalleryImage    __typename  }  events {    ...RestaurantEvent    __typename  }  capabilities  franchiseName  franchiseSlug  geoCoordinate {    latitude    longitude    __typename  }  id  name  phone  temporarilyClosed  timezone  statusValue  serviceHours {    ...RestaurantServiceHours    __typename  }  slug  ...LocationLinks  __typename}fragment BannerImage on ImageSet {  alt  height  url  width  sourceSet(queryList: [{format: WEBP, quality: 50, width: 410}, {width: 410}, {format: WEBP, quality: 50, width: 820}, {width: 820}, {format: WEBP, quality: 50, width: 1680}, {width: 1680}]) {    format    url    width    height    __typename  }  __typename}fragment GalleryImage on ImageSet {  alt  height  url  width  sourceSet(queryList: [{format: WEBP, quality: 50, width: 410}, {width: 410}, {format: WEBP, quality: 50, width: 540}, {width: 540}, {format: WEBP, quality: 50, width: 910}, {width: 910}]) {    format    url    width    height    __typename  }  __typename}fragment RestaurantEvent on RestaurantEvent {  startTime  endTime  legal  title  details  anchorId  __typename}fragment LocationLinks on RestaurantInfo {  onlineOrderingLink  cateringLink  careersLink  __typename}fragment Address on Address {  line1  line2  city  state  country  zipCode  __typename}fragment RestaurantServiceHours on RestaurantServiceHours {  restaurantHours {    ...RestaurantServiceWorkingHour    __typename  }  deliveryHours {    ...RestaurantServiceWorkingHour    __typename  }  pickupHours {    ...RestaurantServiceWorkingHour    __typename  }  __typename}fragment RestaurantServiceWorkingHour on RestaurantServiceWorkingHour {  close  day  description  open  special  __typename}"}'
        payload = json.loads(payload)
        r2 = session.post('https://api.burgerblaster.io/graphql', headers=headers2, data=json.dumps(payload))
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"line1":' in line2:
                add = line2.split('"line1":"')[1].split('"')[0]
                try:
                    add = add + ' ' + line2.split('"line2":"')[1].split('"')[0]
                    add = add.strip()
                except:
                    pass
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                country = 'US'
                zc = line2.split('"zipCode":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(',')[0]
                lng = line2.split('"longitude":')[1].split(',')[0]
                store = line2.split('"id":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                name = line2.split('"name":"')[1].split('"')[0]
                days = line2.split('"restaurantHours":[')[1].split(']')[0].split('"close":"')
                for day in days:
                    if '"day":"' in day:
                        hrs = day.split('"day":"')[1].split('"')[0] + ': ' + day.split('"open":"')[1].split('"')[0] + '-' + day.split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
