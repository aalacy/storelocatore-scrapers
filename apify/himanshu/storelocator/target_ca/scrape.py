import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 100
    zip_code = search.next_zip()

    
    return_main_object = []
    addresses = []
    store_name=[]
    store_detail=[]
  

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "content-type": "application/json;charset=UTF-8",
  
        
    }
    address=[]
    while zip_code:
        try:
            r = session.get(
                'https://redsky.target.com/v3/stores/nearby/'+ str(zip_code) +'?key=eb2551e4accc14f38cc42d32fbc2b2ea&limit='+str(MAX_RESULTS)+'&within='+str(MAX_DISTANCE)+'&unit=kilometer',
                headers=headers,
        
            )
            soup= BeautifulSoup(r.text,"lxml")
            result_coords = []
            k = json.loads(soup.text)
        except:
            continue



        # if k !=[]:
        time =''
        if k != None and k !=[]:
            
            for i in k:
               
                current_results_len = len(i['locations'])  # need to update with no of count.
                
    
                for j in i['locations']:

                    tem_var=[]
                    page_url = 'https://www.target.com/sl/' + j['location_names'][0]['name'].lower().replace(' ','-') + '/' + str(j['location_id'])

                    h1 = j['rolling_operating_hours']['regular_event_hours']['days'][0]['hours'][0]
                    if 'begin_time' in h1 and 'end_time' in h1:
                        hours_of_operation = h1['begin_time'] + " - " + h1['end_time']
                    else:
                        hours_of_operation = "<MISSING>"

                    # for h in h1:
                    #     if 'begin_time' in h['hours'][0] and 'end_time' in  h['hours'][0]['end_time']:
                    #         time = h['hours'][0]['begin_time']+ ' '+ h['hours'][0]['end_time']
                    # exit()
                    tem_var.append("https://www.target.ca")
                    street  = j['address']['address_line1']
                    if street in addresses:
                        continue
                    addresses.append(street)
                    tem_var.append(j['location_names'][0]['name'] if j['location_names'][0]['name'] else "<MISSING>" )
                    tem_var.append(street if street else "<MISSING>" )
                    tem_var.append(j['address']['city'].strip() if j['address']['city'].strip() else "<MISSING>")
                    tem_var.append(j['address']['region'] if j['address']['region'] else "<MISSING>")
            

                    tem_var.append(j['address']['postal_code'] if j['address']['postal_code']  else "<MISSING>")
                    if 'county' in j['address']:
                        tem_var.append('US')
                    else:
                        tem_var.append('US')
                    tem_var.append(j['location_id'] if j['location_id'] else "<MISSING>")
                       
                    tem_var.append(j['contact_information']['telephone_number'] if j['contact_information']['telephone_number'] else "<MISSING>")
                    tem_var.append('target ' + j['type_description'] if 'target ' + j['type_description'] else "<MISSING>")
                    result_coords.append((j['geographic_specifications']['latitude'], j['geographic_specifications']['longitude']))
                    tem_var.append(j['geographic_specifications']['latitude'] if j['geographic_specifications']['latitude'] else "<MISSING>" )
                    tem_var.append(j['geographic_specifications']['longitude'] if j['geographic_specifications']['longitude'] else "<MISSING>" )
                    tem_var.append(hours_of_operation if hours_of_operation else "<MISSING>" )
                    tem_var.append(page_url if page_url else "<MISSING>")
                    
                    

                    yield tem_var

                    # yield store
                if current_results_len < MAX_RESULTS:
                   # print("max distance update")
                    search.max_distance_update(MAX_DISTANCE)
                elif current_results_len == MAX_RESULTS:
                   # print("max count update")
                    search.max_count_update(result_coords)
                else:
                    raise Exception("expected at most " + str(MAX_RESULTS) + " results")
                zip_code = search.next_zip()

            

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



