#!/usr/bin/env python
# coding: utf-8

# In[6]:


import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


# In[7]:



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


# In[8]:


def fetch_data():
    data = []
    base_url = 'http://flagshipcinemas.com/' 
    r = session.get(base_url + 'contactus.html')
    soup = BeautifulSoup(r.text, "lxml")

    locationTable = soup.findAll("table")[0]
    title = soup.find("title")
    title = title.text.strip().split('-')[0].strip()
    contacts = {}
    for location in locationTable.findChildren("td"):    
        loc = location.findAll("p")
        if len(loc) > 0:
            locName = loc[0]
            locPhoneNumber = loc[1]
            contacts[locName.text.strip().split(',')[0].strip().lower()] = locPhoneNumber.text

    addresses = {}
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    for url in soup.findAll("a", {"class": "mm2-menuLink"}):
        cityName = ""
        if url.text.lower().strip() != "film fanatic" and url.text.lower().strip() != "get tickets" and url.text.lower().strip() != "home":
            if url["href"] != "#":
                address_direction = "" 
                address_dir_link = "" 
                link = url["href"]
                loc_r = session.get(link)
                loc_soup = BeautifulSoup(loc_r.text, "lxml")
                dir_img = loc_soup.find("img", {"alt": "directions"})
                if dir_img != None:
                    address_link = base_url + dir_img.find_parent("a")["href"]
                    dir_req = session.get(address_link)
                    dir_soup = BeautifulSoup(dir_req.text, "lxml")
                    dt = dir_soup.find("iframe").find_parent()
                    if dt.find_next_siblings()[0].text.strip() == "": 
                        address = dt.find_next_siblings()[1].text.strip()
                        if address == "":
                            address = dt.find_previous_siblings()[0].text.strip()
                    else:
                        address = dt.find_next_siblings()[0].text.strip()
                    if len(address.split(" at ")) > 1:
                        address = address.split(" at ")[1].split(" in ")[0]
                    else:
                        address = address.split(" at ")[0]
                    address_direction = address
                    address_dir_link = address_link
                    cityName = dir_soup.find("div").find_next_siblings()[0].text.split(",")[0].replace("Flagship Cinemas ","").replace("Flagship Premium Cinemas ","").lower().strip()
                else:
                    if("tritonmovies" in link):
                        link_split = link.split("/")
                        address_link = "http://" + "/".join(link_split[2:-1]) + "/" + loc_soup.find("img",{"id": "Image7"}).find_parent("a")["href"].replace(" ","%20")
                        req_r = session.get(address_link)
                        dir_r = BeautifulSoup(req_r.text, "lxml")
                        dts = dir_r.findAll("font")
                        addr = dts[len(dts)-1].text
                        address_direction = addr
                        address_dir_link = address_link
                    else:
                        address_link = link + "information.html"
                        req_R = session.get(address_link)
                        dir_R = BeautifulSoup(req_R.text, "lxml")
                        dtS = dir_R.findAll("span", {"class": "textcolor"})
                        addr = dtS[len(dtS) - 1].text
                        address_direction = addr
                        address_dir_link = address_link
                    splits = address_direction.split(",")[0].split(" ")
                    cityName = splits[len(splits) - 1].strip().lower()
                    if cityName == 'chincoteague':
                        cityName = 'chincotegue'
                addresses[cityName] = address_direction
    for key in contacts:
        row = []
        #locator_domain
        row.append(base_url)
        #location_name
        row.append('Flagship Cinemas-' + title)
        #street Address
        full_addr = addresses[key].replace(",","").replace(".","")
        full_addr_split = full_addr.split(" ")
        street_addr = " ".join(full_addr_split[:-2])
        zipcode = full_addr_split[len(full_addr_split) - 1]
        statecode = full_addr_split[len(full_addr_split) - 2]
        row.append(street_addr)
        #city
        row.append(key)
        #state
        row.append(statecode)
        #zip
        row.append(zipcode)
        #country_code
        row.append('US')
        #store number
        row.append('<MISSING>')
        #phone number
        row.append(contacts[key])
        #location_type
        row.append("Flagship Cinemas")
        #longitute
        row.append('<INACCESSIBLE>')
        #latitude
        row.append('<INACCESSIBLE>')
        #hours_of_operation
        row.append('<MISSING>')
        data.append(row)
    return data


# In[9]:


def scrape():
    data = fetch_data()
    write_output(data)
scrape()

