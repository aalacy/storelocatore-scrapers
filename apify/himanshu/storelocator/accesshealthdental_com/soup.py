import requests
from bs4 import BeautifulSoup
import re

base_url = "http://accesshealthdental.com/locations.php"
r = requests.get(base_url)
soup = BeautifulSoup(r.text,"lxml")
k = soup.find("table",{"width":"620",'cellspacing':"0",'cellspacing':"0",'border':"0"}).td
store_names = []
for name in k.find_all('h3'): 
    store_names.append(name.text.strip(' \n\t'))
store_details = []
for i in k.find_all('p'):
    lat_lgt=''
    if(i.a != None):
        a = (i.find_all('a') [len(i.find_all('a')) - 1])
        k=a['href'].split('ll=')
        if len(k)==2 or len(k)==3:
            lat_lgt= lat_lgt + (k[1].split('&')[0])
        k=a['href'].split('@')
        if len(k)==2:
            lat_lgt = lat_lgt+(k[1].split('m')[0])
        if len(k)==1 and len(a['href'].split('ll='))!=2 and len(a['href'].split('ll='))!=3  :
            lat_lgt = lat_lgt+"<MISSING>,<MISSING>"
    else:
         lat_lgt = lat_lgt + '<MISSING>,<MISSING> '
    lat_lgt1=lat_lgt.split(',')
    temp_var = []
    temp = list(i.stripped_strings)
    ds =temp[1].split(',',2)
    if temp[1].count(",") == 2:
        store_number = temp[1].split(",")[0]
        temp[0] = temp[0] + store_number
        temp[1] = ','.join(temp[1].split(",")[1:])
    street_address=temp[0]
    city_zip = temp[1].split(',')
    city = city_zip[0]
    state = city_zip[1].split()[0]
    zipcode  = city_zip[1].split()[1]
    phone = temp[2].split('p:')[1].replace(" ", "")
    atitude = lat_lgt1[0]
    longitude = lat_lgt1[1]
    temp_var.append(street_address)
    temp_var.append(city)
    temp_var.append(state)
    temp_var.append(zipcode)
    temp_var.append("US")
    temp_var.append("<MISSING>")
    temp_var.append(phone)
    temp_var.append("<MISSING>")
    temp_var.append(atitude)
    temp_var.append(longitude)
    temp_var.append("<MISSING>")
    store_details.append(temp_var)
main_object = []

for i in range(len(store_names)):
    store= list()
    store.append("http://accesshealthdental.com")
    store.append(store_names[i])
    store.extend(store_details[i])
    main_object.append(store)

print(main_object)
