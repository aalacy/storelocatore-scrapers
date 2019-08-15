from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression

country_codes={
    'Chile':"CL",'Poland':"PL", 'Switzerland':"CH", 'Mexico':"MX", 'India':"IN", 'Australia':"AU", 'Austria':"AT", 'Philippines':"PH", 'USA':"US",
    'United States':"US", 'Canada':"CA", 'Jamaica':"JM",'Czech Republic':"CZ", 'France':"FR", 'Peru':"PE", 'Germany':"DE",
    'Scotland':"GB", 'Norway':"NO", 'Belgium':"BL", 'Hanover, Massachusetts':"<MISSING>", 'Argentina':"AR",
    'KENYA':"KE",'Italy':"IT",'Japan':"JP",'Spain':"ES",
    }


opts=Options()
opts.add_argument("ignore-certificate-errors")
capabilities = webdriver.DesiredCapabilities.CHROME
driver=webdriver.Chrome('C:\\Users\\Lenovo\\Desktop\\chrome-driver\\chromedriver',options=opts,desired_capabilities=capabilities)
driver.implicitly_wait(80)
url= "https://www.bikramyoga.com/studios/studio-locator/"
locator_domain=url
driver.get(url)
time.sleep(5)
html = driver.execute_script("return document.body.innerHTML")
soup = BeautifulSoup(html,"html.parser")
country_st= {""}
location_n = soup.find_all('span',attrs={"class":"location_name"})
#for x in location_n:
 #   location_name=location_name+x.text

all_rec = soup.find_all('div',attrs={"class":"results_row_center_column location_secondary"})
with open("data.csv",mode="a+") as file:
    fl_writer=csv.writer(file,delimiter='^')
    i=0
    for x in all_rec:
        location_name=location_n[i].text
        i=i+1
        street_address=""
        city=""
        state=""
        zip_code=""
        country_code=""
        store_number=""
        phone=""
        location_type=""
        latitude=""
        longitude=""
        hours_of_operation=""
        f = x.text.split("\n")
        complete_record=[]
        #print("Length is ",len(f))
        for y in f:
            if len(y) > 2:
                complete_record.append(y)
        if len(complete_record)==2:
            #print("length is 2")
            street_address= complete_record[0]
            state = complete_record[1]
        elif len(complete_record )==3:
            street_address=complete_record[0]
            if re.search('\d',str(complete_record[2])): #if third record is a number , it means second is country
                #print("country ",complete_record[1])
                country = complete_record[1]
                #country_st.add(complete_record[1])
                phone=complete_record[2]
            else: #if it not a number , then last is the country and second is the state and may contain zip
                #print("state ",complete_record[1])
                country=complete_record[2]
                #country_st.add(complete_record[2])
                second_split = str(complete_record[1]).split(",") #split second record with ,
                if len(second_split) == 2: #if it can be split into two , then it means, first one is the city and second is state, and may contain zip
                    city =second_split[0]
                    cp = second_split[1].split() #now further split it , to check whether it contains zip
                    if len(cp)==2:
                        state =cp[0]
                        zipp_code = cp[1]
                    else:
                        state = cp[0]
                #else:
                 #   print("country = ", str(second_split[0]))
        elif len(complete_record) == 4:
            street_addreess =complete_record[0]
            second_split = str(complete_record[1]).split(",") #split second record with ,
            if len(second_split) == 2: #if it can be split into two , then it means, first one is the city and second is state, and may contain zip
                    city = second_split[0]
                    cp = second_split[1].split() #now further split it , to check whether it contains zip
                    if len(cp)==2:
                        state =cp[0]
                        zipp_code = cp[1]
                    else:
                        state = cp[0]
            elif len(second_split)==3:
                if(re.search('\d',str(second_split[2]))):
                    city = str(second_split[0])+str(second_split[1])
                    cp = second_split[2].split() #now further split it , to check whether it contains zip
                    if len(cp)==2:
                        state=cp[0]
                        zip_code = cp[1]
                    else:
                        state = cp[0]
            country = complete_record[2]
            #country_st.add(complete_record[2])
            phone = complete_record[3]
        else:
            street_address=str(complete_record[0])+str(complete_record[1])+str(complete_record[2])
            country=str(complete_record[3])            #country_st.add(complete_record[3])
            #print("code ", str(complete_record[4]))
        if country!="":
            country_code=country_codes[country]
        else:
            country_code="<MISSING>"
        if locator_domain == "":
            locator_domain="<MISSING>"
        if location_name=="":
            location_name="<MISSING>"
        if street_address=="":
            street_address ="<MISSING>"
        if city=="":
            city="<MISSING>"
        if state=="":
            state="<MISSING>"
        if zip_code=="":
            zip_code="<MISSING>"
        if country_code=="":
            country_code="<MISSING>"
        if store_number == "":
            store_number="<MISSING>"
        if phone=="":
            phone="<MISSING>"
        if location_type=="":
            location_type="<MISSING>"
        if latitude=="":
            latitude="<MISSING>"
        if longitude=="":
            longitude="<MISSING>"
        if hours_of_operation=="":
            hours_of_operation="<MISSING>"
        data=[]
        data.extend((locator_domain.encode("utf-8"),location_name.encode("utf-8"),street_address.encode("utf-8"),city.encode("utf-8"),
                     state.encode("utf-8"),zip_code.encode("utf-8"),country_code.encode("utf-8"),store_number.encode("utf-8"),
                     phone.encode("utf-8"),location_type.encode("utf-8"),latitude.encode("utf-8"),longitude.encode("utf-8"),
                     hours_of_operation.encode("utf-8")))
        fl_writer.writerow(data)
             
driver.quit()
    
