import csv
import re
import requests
import time
import sgzip


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    countries=[]
    
    
    MAX_RESULTS = 10
    MAX_DISTANCE = 100.0
    key_set=set([])
    all=[]
    op=["5655","5656"]
    for o in op:
        
        search=sgzip.ClosestNSearch()
        search.initialize()
        coord = search.next_coord()
        while coord:

            code=search.current_zip
        #
            #print(code)
        #continue
            al="addressline="+str(code)+"&r=100&storetype="+o
            url="https://local.pavilions.com/search.html?"+al
            headers = {
    'accept': 'application/json',
    'accept - encoding': 'gzip, deflate, br',
    'accept - language': 'en-US,en;q=0.9',
    'referer': 'https://local.pavilions.com/search.html?'+al,
    'sec - fetch - mode': 'cors',
    'sec - fetch - site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'}
            r = requests.get(url,headers=headers,data=al)
            try:
                results=r.json()['locations']
            except:
                results=[]
            result_coords = []
            for r in results:
                
                if r['loc']['hours']['days']==[]:
                    tim="<MISSING>"
                else:
                    day_list = r['loc']['hours']['days']
                    tim=""
                    for day in day_list:
                       tim += day['day'].replace(",","")+" "+str(day['intervals'][0]).replace(",","")+" "
                    
                la =r['loc']['latitude']
                lo =r['loc']['longitude']
                result_coords.append((la, lo))
                if la==None:
                   la="<MISSING>"
                if lo==None:
                   lo="<MISSING>"
                st=r['loc']['address1']+" "+r['loc']['address2'].strip()
                st=st.replace(",","").replace(",","")
                c=r['loc']['city'].replace(",","")
                s=r['loc']['state'].replace(",","")
                s=s.replace(",","").replace(",","")
                country=r['loc']['country'].replace(",","")
                l=r['loc']['name'].replace(",","")
                z=r['loc']['postalCode'].strip().replace(",","")
                if z=="":
                     z="<MISSING>"
                ph=r['loc']['phone']
                if ph=="":
                     ph="<MISSING>"
                ty=r['loc']['customByName']['Store Type'].replace(",","")
                if r['loc']['customByName']['Has Pharmacy'] == 'True':
                    ty+= " "+"Pharmacy"
                
                id = r['loc']['customByName']['OldStoreID']
                if str(type(id))=="<class 'NoneType'>":
                    id="<MISSING>"
                else :
                    id=id.replace(",","")
                #print(type(id),type(ty))
                key = st+"," +c+"," +s+"," +z

                #row="https://www.pavilions.com,"+l+"," +st+"," +c+"," +s+"," +z+"," +country+"," +id+"," +ph+"," +ty+"," +str(la)+"," +str(lo)+"," +tim+"," +url
                if key not in key_set:
                    key_set.add(key)
                    locs.append(l)
                    street.append(st)
                    states.append(s)
                    cities.append(c)
                    types.append(ty)
                    phones.append(ph)
                    zips.append(z)
                    long.append(str(lo))
                    lat.append(str(la))
                    timing.append(tim)
                    ids.append(id)
                    page_url.append(url)
                    countries.append(country)
            if len(results) < MAX_RESULTS:
                #print("max distance update")
                search.max_distance_update(MAX_DISTANCE)
            elif len(results) == MAX_RESULTS:
                #print("max count update")
                search.max_count_update(result_coords)
        #break
            coord = search.next_coord()
            #code=search.current_zip

    
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.pavilions.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all
    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

