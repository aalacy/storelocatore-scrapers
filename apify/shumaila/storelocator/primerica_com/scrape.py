
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []    
    p = 0
    url = 'http://www.primerica.com/public/locations.html'
    page = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    maidiv = soup.find('main')
    mainsection = maidiv.findAll('section',{'class':'content locList'})
    #print(len(mainsection))
    sec = 0
    while sec < 2:
        if sec == 0:
            ccode = "US"
        if sec == 1:
            ccode = "CA"
        rep_list = mainsection[sec].findAll('a')       
        cleanr = re.compile('<.*?>')
        pattern = re.compile(r'\s\s+')
        for rep in rep_list:            
            link = "http://www.primerica.com/public/" + rep['href']            
            #print(link)           
            try:
               
                page1 = session.get(link, headers=headers, verify=False)                    
                time.sleep(1)
                soup1 = BeautifulSoup(page1.text, "html.parser")
                maindiv = soup1.find('main')
                xip_list = maindiv.findAll('a')
                print("len = ",len(xip_list))
               
                for xip in xip_list:                    
                    try:
                        pcode = xip.text
                        #print('http://www.primerica.com'+xip['href'])
                        page2 = session.get('http://www.primerica.com'+xip['href'], headers=headers, verify=False)                    
                        time.sleep(1)
                        soup2 = BeautifulSoup(page2.text, "html.parser")                   
                        mainul = soup2.find('ul',{'class':'agent-list'})
                        li_list = mainul.findAll('li')
                        #print(len(li_list))
                        for m in range(0, len(li_list)):
                            try:
                                address = ''
                                alink = li_list[m].find('a')                       
                                title = alink.text
                                alink = alink['href']
                                
                                #print(alink)
                                page3 = session.get(alink, headers=headers, verify=False)                    
                                time.sleep(1)
                                soup3 = BeautifulSoup(page3.text, "html.parser")                            
                                address = soup3.find('div',{'class':'officeInfoDataWidth'})
                                cleanr = re.compile(r'<[^>]+>')
                                address = cleanr.sub(' ', str(address))
                                address = re.sub(pattern,' ',address).lstrip()
                                #print(address)
                                addrm = address
                                address = usaddress.parse(address)
                                i = 0
                                street = ""
                                city = ""
                                state = ""
                                pcode = ""
                                while i < len(address):
                                    temp = address[i]
                                    if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                                        "USPSBoxID") != -1:
                                        street = street + " " + temp[0]
                                    if temp[1].find("PlaceName") != -1:
                                        city = city + " " + temp[0]
                                    if temp[1].find("StateName") != -1:
                                        state = state + " " + temp[0]
                                    if temp[1].find("ZipCode") != -1:
                                        pcode = pcode + " " + temp[0]
                                    i += 1

                               
                                
                                
                                phone = soup3.find('div',{'class':'telephoneLabel'}).text
                                phone = phone.replace('Office: ','')
                                phone = phone.replace("Mobile","")
                                phone = phone.replace(":","")
                                phone = phone.strip()
                                if len(phone) < 2:
                                    phone = "<MISSING>"
                                if len(street) < 2 :
                                    street = "<MISSING>"
                                if len(city) < 2:
                                    city  = "<MISSING>"                        
                                if len(state) < 2 :
                                    state = "<MISSING>"

                                if len(pcode) < 2:
                                    pcode = "<MISSING>"

                                if len(phone) < 11:
                                    phone = "<MISSING>"
                                i = 0
                                flag = True
                                if len(state) > 2 and state !="<MISSING>" and  pcode == "<MISSING>":
                                    print('enter')
                                    state = state.lstrip()
                                    state = state[0:2]
                                    pcode = addrm[addrm.find(state)+2:len(addrm)]
                                if state == "<MISSING>" and  pcode == "<MISSING>" or len(pcode) < 5:
                                    print("YES")
                                    street,state = addrm.split(', ')
                                    state = state.lstrip()
                                    state,pcode = state.split(' ',1)
                                    pcode = pcode.lstrip()
                                    temp = []
                                    city = street.split(' ')[-1]
                                    #city = temp[-1]
                                    street = street.replace(city,'')
                                    
                                street = street.lstrip().replace(',','')
                                city = city.lstrip().replace(',','')
                                state = state.lstrip().replace(',','')
                                pcode = pcode.lstrip().replace(',','')
                                try:
                                    for i in range(0,len(data)):                                        
                                        #print(i, pcode,data[i][6])
                                        if pcode == data[i][6]:
                                            #print("exist")
                                            flag = False
                                            break
                                    
                                except Exception as e:
                                    print(e)
                                if state == "NF":
                                    state = "NL"
                                if state == "PQ":
                                    
                                    state = "QC"
                                if flag:
                                    data.append([
                                            'http://www.primerica.com/',
                                            alink,
                                            title,
                                            street,
                                            city,
                                            state,
                                            pcode.rstrip(),
                                            ccode,
                                            "<MISSING>",
                                            phone,
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                        ])
                                    
                                #print(street,city,state,pcode,phone)
                                    #print(p,data[p])
                                    p += 1
                                    #input()
                                #input()
                                
                            except Exception as e:
                                print(e)
                                pass
                               
                    except Exception as e:
                        print(e)
                        pass
                        


                    #break
            except Exception as e:
                print(e)
                pass

            #driver1.quit()
            #break
        sec += 1
        #if sec == 1:
            #break

    return data




def scrape():

    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
