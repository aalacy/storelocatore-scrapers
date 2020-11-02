import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import re
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }




def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
   
    mainlink = []
    data=[]
    p = 0
    mainlink.append("https://www.topshop.com/store-locator?country=United+States")
    mainlink.append("https://www.topshop.com/store-locator?country=Canada")

    for t in range(1,len(mainlink)):
        link = mainlink[t]
        print(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
    
        mainlist = soup.findAll('div',{'class':'Store'})
        print(len(mainlist))
   
        for i in range(0,len(mainlist)):
            if t == 0:
                ccode = 'US'
            elif t == 1:
                ccode = 'CA'
            print(ccode)
            main = mainlist[i].find('script').text
            main= json.loads(main)
            try:
                location_name=main['name']
                if location_name =="":
                    location_name = '<MISSING>'
            except:
                location_name='<MISSING>'
            try:
                op_hrs=str(main['openingHours'])
                empty_hrs = bool(re.search(r'\d',op_hrs))
                if empty_hrs == False:
                    op_hrs = '<MISSING>'
                else:
                    op_hrs = op_hrs.replace("{","").replace("}","").replace("'","").replace(","," ")
            except:
                op_hrs='<MISSING>'
            try:
                store_number=main['storeId']
                if store_number =="":
                    store_number = '<MISSING>'
            except:
                store_number='<MISSING>'
            try:
                phno=main['telephoneNumber'].replace("(+00)","").replace("(+001)","")
                if phno =="":
                    phno = '<MISSING>'
            except:
                phno='<MISSING>'
            try:
                lng1=main['longitude']
                if lng1 =="" or lng1 == 0:
                    lng1 = '<MISSING>'
            except:
                lng1='<MISSING>'
            try:
                lat1=main['latitude']
                if lat1 =="" or lat1 == 0:
                    lat1 = '<MISSING>'
            except:
                lat1='<MISSING>'

            title = mainlist[i].find('h2',{'class':'Store-name'}).text
            location_name = 'Topshop '+ location_name 
            print(title,location_name)
            if ccode == 'US':
                
                address = mainlist[i].findAll('span',{'class':'Store-address'})
                print(len(address))
                '''for addr in address:
                    print(addr.text)
                    input()'''
                try:
                    street = address[0].text
                    if street.find('Nordstrom') > -1 :
                        street = address[1].text
                        state = address[2].text
                        pcode = address[3].text
    
                    else:
                        state = address[1].text
                        pcode = address[2].text

                    try:
                        city,state = state.split(',')
                        if len(state) < 2:
                            state = "<MISSING>"
                            
                    except:
                        city = state
                        state = "<MISSING>"
                   
                    
                except:
                    
                    street = address[0].text
                       

                    
                if city == '0':
                    try:
                        city = main["addresslocality"]
                        city = city.replace(',','')
                        if city == '0':
                            city = "<MISSING>"
                    except:
                        city = "<MISSING>"
                if len(pcode) < 4:
                    print('yes')
                    try:
                        pcode = main["postalCode"]
                        pcode = pcode.replace(',','')
                        if pcode == '0':
                            pcode = "<MISSING>"
                    except:
                        pcode = "<MISSING>"

                street = street.replace(',','')
                if len(pcode) < 5:
                    pcode = '0'+ pcode
            elif ccode == 'CA':
                
                address = mainlist[i].findAll('span',{'class':'Store-address'})
                #print(main['address'])
                print(len(address))
                try:
                    print('1')
                    pcode = '<MISSING>'
                    try:
                        print(main['addressLocality'])
                    except:
                        print(main['address'])
                        main = main['address']
            
                    check = main['addressLocality']
                    print(check)
                    temps =[]  
                    if len(check)< 3:
                        print('pcode')
                        state = main['addressLocality']
                        street = main['streetAddress']
                        temps = street.split(',')
                        if len(temps) == 2:
                            street = temps[0]
                            city = temps[1]
                        elif len(temps) == 3:
                            street = temps[0] + ' ' +temps[1]
                            city = temps[2]
                        pcode = "<MISSING>"
                    elif len(check) == 7 :
                        temp1,temp2 = check.split(' ')
                        if len(temp1) == 3 and len(temp2) == 3:
                            pcode = main['addressLocality']
                            street = main['streetAddress']
                            temps = street.split(',')
                            print("temps=",len(temps))
                            if len(temps) == 3:
                                street = temps[0]
                                city = temps[1]
                                state = temps[2]
                                if len(state) > 3:
                                    state = state.lstrip()
                                    mn = state.split(' ')
                                    street = street + ' ' +city
                                    city = mn[0]
                                    state = mn[1]
                            
                            elif len(temps)== 4:
                                street = temps[0] + ' ' + temps[1]
                                city = temps[2]
                                state = temps[3]
                            
                    else:
                        city = main['addressLocality']
                        try:
                            
                            temps = city.split(' ')
                            print('hhhhhhhhhhhhhh',len(temps),len(temps[0]))
                            if len(temps) > 2:
                                print('ttttttttttttttttt')
                                state = temps[0]
                                try:
                                    pcode = temps[1]+temps[2]+ temps[3]
                                except:
                                    pcode = temps[1]+' '+temps[2]
                                temp2s = main['streetAddress'].split(',')
                                if len(temp2s) == 2:
                                    street = temp2s[0] + ' ' + temp2s[1]
                                    city = "<MISSING>"
                                elif len(temps) == 3:
                                    try:
                                        mm = []
                                        mm = temp2s[1].split(' ')
                                        street = temp2s[0] + ' ' + temp2s[1]
                                        city =  temp2s[2]
                                    except:
                                        street = temp2s[0]
                                        city = temp2s[1]
                                if state == 'Canada':
                                    try:
                                        city = city.lstrip()
                                        temps = city.split(' ')
                                        city= temps[0]
                                        state = temps[1]
                                    except:
                                        pass
                            
                        except:
                            
                            temps = main['streetAddress'].split(',')
                            if len(temps) == 2:
                                state = "<MISSING>"
                                pcode ="<MISSING>"
                                street = main['streetAddress']
        
                               
                            elif len(temps)== 4 :
                                street = temps[0]
                                city = temps[1]
                                state = temps[2]
                                pcode = temps[3]
                            elif len(temps)== 3:
                                if len(temps[2]) > 3:
                                    street = temps[0] + ' ' + temps[1]
                                    city = temps[2]
                                else:
                                    street = temps[0] 
                                    city = temps[1]
                                    state = temps[2]
                                   
                                
                           
                            print("HRE")
                            
                except:
                    print('2')
                    try:
                        street = address[0].text
                    except:
                        try:
                            street = main['streetAddress']
                        except:
                            street = "<MISSING>"
                    try:
                        city = address[1].text
                    except:
                        city = "<MISSING>"
                    try:
                        
                        state = address[2].text
                        if len(state) == 3:
                            state = '<MISSING>'
                    except:
                        state = '<MISSING>'
                        

            street = street.lstrip()
            state = state.lstrip()
            city = city.lstrip()
            pcode = pcode.lstrip()
            state = state.rstrip().replace(',','')
            if pcode == '<MISSING>':
                try:
                    pcode = main['postalCode']
                except:
                    pcode = '<MISSING>'
            if city == '<MISSING>' or city == '' and len(state) > 2:
                try:
                    state = state.lstrip()
                    temps = state.split(' ')
                    city = temps[0]
                    state = temps[1]
                except:
                    pass
            if city != '<MISSING>' or city != '' and len(state) > 2:
                try:
                    state = state.lstrip()
                    temps = state.split(' ')
                    
                    state = temps[1]
                except:
                    pass                
           
            print(street,state,pcode)
            data.append([
                     'www.topshop.com',
                     link,
                     location_name,
                     street,
                     city,
                     state,
                     pcode,
                     ccode,
                     store_number,
                     phno,
                     '<MISSING>',
                     lat1,
                     lng1,
                     op_hrs                     
                   ])
            print(p,data[p])
            p += 1
            #input()

    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
