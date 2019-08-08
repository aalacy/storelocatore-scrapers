import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
import pandas as pd
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                #Keep the trailing zeroes in zipcodes
                writer.writerow(row)

def fetch_data():
    #Variables
    data=[];address_stores=[]; city=[];street_address=[];zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = webdriver.Chrome('chromedriver')
    #Get site
    driver.get('http://www.goldendelirestaurant.com/locations/')
    time.sleep(6)
    # Fetch stores location name and links
    hours = driver.find_elements_by_class_name("g1-list--empty")
    hours_of_operation=[hours[i].text for i in range(0,len(hours))]
    street = driver.find_elements_by_tag_name("h2")
    street_address = [street[i].text for i in range(0,len(street))]
    address =driver.find_elements_by_tag_name("h4")
    for n in range(0,len(address),2):
        city.append(address[n].text.split(",")[0])
        zipcode.append(address[n].text.split(",")[1].strip().split()[-1])
        state.append(address[n].text.split(",")[1].strip().split()[0])
    for n in range(1,len(address),2):
        phone.append(address[n].text)
    for n in range(0,len(street)): 
        data.append([
            'https://www.crayolaexperience.com',
            '<MISSING>',
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
    #Removing empty lines in csv
    #df = pd.read_csv("data.csv", sep=",")
    #df.drop_duplicates(subset =["location_name","street_address","city","state","zip","country_code","store_number","phone"]
                     #,keep = False, inplace = True)
    #df.to_csv("data.csv")

scrape()
