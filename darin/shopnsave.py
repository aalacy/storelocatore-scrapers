import urllib2
import time
import os
import re
import csv

path = '.'  ### this is a relative path for where the output file will be put

header = 'locator_domain,location_name,street_address,city,state,zip,country_code,store_number,phone,location_type,naics_code,latitude,longitude,hours_of_operation\n'
with open("%s/ShopNSave.csv" % path, "wb") as out_file:
            out_file.write(header)

domain = 'https://www.shopnsavefood.com'

url = 'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores'
page_text = urllib2.urlopen(url)
for line in page_text:
    if '<StoreID>' in line:
        hid = line.split('>')[1].split('<')[0].replace('"',"'")
        name = ''
        add = ''
        city = ''
        zc = ''
        state = ''
        phone = ''
        lat = ''
        lng = ''
        hrs = ''
        brand = ''
    if '<Name>' in line:
        name = line.split('>')[1].split('<')[0].replace('"',"'")
    if '<Address1>' in line:
        add = line.split('>')[1].split('<')[0].replace('"',"'")
    if '<City>' in line:
        city = line.split('>')[1].split('<')[0].replace('"',"'")
    if '<State>' in line:
        state = line.split('>')[1].split('<')[0].replace('"',"'")
    if '<Zip>' in line:
        zc = line.split('>')[1].split('<')[0].replace('"',"'")
    country = 'US'
    if '<Phone>' in line:
        phone = line.split('>')[1].split('<')[0].replace('"',"'")
    if '<Latitude>' in line:
        lat = line.split('>')[1].split('<')[0].replace('"',"'")
    if '<Longitude>' in line:
        lng = line.split('>')[1].split('<')[0].replace('"',"'")
    if '<Hours>' in line:
        hrs = line.split('>')[1].split('<')[0].replace('"',"'")
    if '<Hours2>' in line:
        hrs = hrs + ', ' + line.split('>')[1].split('<')[0].replace('"',"'")
    if '<IsGasStation>true' in line:
        brand = 'Fuel'
    if '<IsGasStation>false' in line:
        brand = 'Store'
    if '</Store>' in line:
        info = '"' + domain + '","' + name + '","' + add + '","' + city + '","' + state + '","' + zc + '","' + country
        info = info + '","' + hid + '","' + phone + '","' + brand + '","","' + lat + '","' + lng + '","' + hrs + '"'
        info = info.replace('\n','').replace('\r','').replace('&amp;','&')
        with open("%s/ShopNSave.csv" % path, "ab") as out_file:
            out_file.write(info + '\n')
