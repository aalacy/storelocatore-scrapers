import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    # zips = sgzip.for_radius(100)
    # zips =sgzip.coords_for_radius(50)

    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
   

    }

    # it will used in store data.
 
    while coord:
        result_coords = []
        # data = '{"strLocation":"85029","strLat":33.5973469,"strLng":-112.10725279999997,"strRadius":"100","country":"US"}'
        # print("zips === " + str(zip_code))
        #print(coord)
        try:
            r = requests.get(
                'https://www.imax.com/showtimes/ajax/theatres?date=2019-09-13&lat='+str(coord[0])+'&lon='+str(coord[1]),
                headers=headers)
        except:
            continue
        soup1= BeautifulSoup(r.text,"lxml").text
        k = json.loads(soup1)
        current_results_len =len(k['rows'])
        for i in k['rows']:
            tem_var=[]
            lat = i['location'].split(',')[0]
            lon = i['location'].split(',')[1]
            soup2= BeautifulSoup(i['row'],"lxml")
            name = list(soup2.stripped_strings)[0]
            v1 = list(soup2.stripped_strings)
            v2 = list(soup2.stripped_strings)[1].split(',')
            time1 = " ".join(v1[-3:]).split(',')
            time2 = ''
            
            if len(time1)!=1:
                time = "<MISSING>"
            else:
                time = time1[0].replace("IMAX®","")

            if len(time.split( ))==3 or len(time.split( ))==1:
                time2 = " ".join(time.split( )).replace("2D","").strip()
            else:
                time2 = "<MISSING>"
           
            if len(v2)==5:
                st = " ".join(v2[0:2])
                city  = v2[3].strip()
                state1 = v2[4].strip().split( )[0]
                zip1 = v2[4].strip().split( )[-1]
                # print("55555555555   ",zip1)
             
            elif len(v2)==3:
                st = v2[0]
                city  = v2[1].strip()
                state = v2[2].strip().split( )[0]
                state1 =''
                if len(v2[2].strip().split( ))==2:
                    
                    state1 = (v2[2].strip().split( )[0])
                    zip1 = v2[2].strip().split( )[1]

                elif len(v2[2].strip().split( ))==3:
                    state = v2[2].strip().split( )
                    
                    if len(state)==3:
                        if len(state[1])!=3:
                            state1 = (" ".join(state[:2]))
                        else:
                            state1 = state[0]
                    else:
                        state1 = state[0]
                    zip1 = " ".join(v2[2].strip().split( )[1:]).replace("Jersey","").replace("Zealand 1005","<MISSING>").replace("and Tobago","")
                    
                elif len(v2[2].strip().split( ))==1:
                    state1 = v2[2].strip().split( )[0]
                    zip1 = "<MISSING>"
                # zip1 = v2[2].strip().split( )[1]
                
                # print("33333333333   ",zip1)
            elif len(v2)==4:
                if "Canada" in  v2[-1].strip():
                    state = " ".join(v2[-2:]).strip().replace("Canada","").split('  ')[0]
                    zip1 = " ".join(v2[-2:]).strip().replace("Canada","").split('  ')[-1]
                    city = v2[-3].strip()
                    st = v2[0]
                    # print(" ".join(v2[-2:]).strip().replace("Canada","").split('  ')[-1])
                else:
                    state =v2[-1].strip().split(  )[0]
                    zip1 = v2[-1].strip().split(  )[-1]
                    city = v2[-2].strip()
                    st = " ".join(v2[:2])
                
                # print(v2)
                
                # st = v2[0]
                # city  = v2[1].strip()
                # state1 = v2[2].strip()
                # zip1 = v2[3].strip().replace("Canada","")
                # print("4444444444   ",zip1)
            elif len(v2)==6:
                st = " ".join(v2[0:3])
                city  = v2[4].strip()
                state1 = v2[5].strip().split( )[0]
                zip1 = v2[5].strip().split( )[-1]
                # print("6666666666   ",zip1)
            else:
                # print(v1)
                # print('https://www.imax.com/showtimes/ajax/theatres?date=2019-09-13&lat='+zip_code[0]+'&lon='+zip_code[1])
                st = "<MISSING>"
                city  = v2[0].strip().split(',')[0]
                state1 = v2[1].strip().split( )[0]
                zip1 = v2[1].strip().split( )[1]
                # print("other ===",zip1)

            if len(zip1)==6 or len(zip1)==7:
                c = "CA"
            else:
                c = "US"
            # print(state1)
            tem_var.append("https://www.imax.com/")
            tem_var.append(name if name else "<MISSING>" )
            tem_var.append(st if st else "<MISSING>"  )
            tem_var.append(city if city else "<MISSING>" )
            tem_var.append(state1 if state1 else "<MISSING>" )
            tem_var.append(zip1.replace("York ","").replace("Canada","").replace("720021","<MISSING>") if zip1.replace("York ","").replace("Canada","").replace("720021","<MISSING>") else "<MISSING>" )
            tem_var.append(c)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(lat if lat else "<MISSING>" )
            tem_var.append(lon if lon else "<MISSING>" ) 
            tem_var.append(time2 if time2 else "<MISSING>" )
            tem_var.append("<MISSING>" )
            #print("----------------------------------",tem_var)
            if tem_var[2] in addresses:
                continue
            addresses.append(tem_var[2])
            # print(tem_var)
            yield tem_var

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
    
            # return_main_object.append(tem_var)
  
    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
