import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = 'https://www.petros.com/'
    get_url= "https://www.petros.com/locations/"
    r = session.get(get_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    address1=[]
    store_detail=[]
    return_main_object=[]
    
    k = soup.find_all("div",{"class":"wp-block-column"})
    for i in k:
        p = i.find_all("p")
        for p1 in p:
            tem_var =[]
            if "Section 121" in list(p1.stripped_strings) or "Neyland Stadium" in list(p1.stripped_strings) :
                pass
            else:
                st  = list(p1.stripped_strings)
                if st !=[]:
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(st))
                    if phone_list !=[]:
                        phone = st[-1]
                        city_tmp = st[2].split(',')
                        if (len(city_tmp)==2):
                            location_name = st[0]
                            address = st[1]
                            city_tmp = st[2].split(',')
                            city = city_tmp[0]
                            state_tmp = city_tmp[1].strip().split(' ')
                            state = state_tmp[0]
                            zip =state_tmp[1]
                            phone = st[-1]
                            hour = st[4]+ ' '+st[5]+ ' '+st[6].replace(phone,'').replace('*','')

                            
                        else:
                            if(len(st)==7):
                                location_name = st[1]
                                address =st[2]
                                city_tmp =st[3].split(',')
                                city = city_tmp[0]
                                state_tmp = city_tmp[1].strip().split(' ')
                                state = state_tmp[0]
                                zip = state_tmp[1]
                                phone = st[-1]
                                hour = st[4]+ ' '+st[5]
                            else:
                                location_name = '<MISSING>'
                                address = st[0]
                                city_tmp =st[1].split(',')
                                city = city_tmp[0]
                                state_tmp = city_tmp[1].strip().split(' ')
                                state = state_tmp[0]
                                zip = state_tmp[1]
                                phone = st[-1]
                                hour = st[3]+' '+st[4].replace(phone,'').replace('*','')
                                
                       
                 
                tem_var.append(base_url)     
                tem_var.append(location_name)
                tem_var.append(address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zip)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hour)
                tem_var.append(get_url)
                
                if  tem_var[2] in address1:
                    continue
                address1.append(tem_var[2])
                return_main_object.append(tem_var)
   

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
