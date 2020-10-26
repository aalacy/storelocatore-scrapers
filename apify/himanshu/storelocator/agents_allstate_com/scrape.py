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
    base_url= "https://agents.allstate.com/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    # print(soup)
    store_name=[]
    store_detail=[]
    return_main_object=[]
    address123 =[]
    # div  =soup.find("div",{"class":"Directory-listLinks"})
    k= soup.find_all("a",{"class":"Directory-listLink","data-ya-track":"directorylink","data-allstate-web-analytics":"Directory-listLink"})
    k=soup.find_all("a",{"class":re.compile("Directory-listLink")}) 
    # k= div.find_all("ul",{"class":"Directory-letterList"})
    #print(len(k))
    for i in k:
        try:

            r1 = session.get("https://agents.allstate.com/"+i['href'])
        except:
            continue
        soup1= BeautifulSoup(r1.text,"lxml")
        link_state=soup1.find_all("a",{"class":re.compile("Directory-listLink")}) 
        for link in link_state:
            
            #print("city========================","https://agents.allstate.com"+link['href'].replace("..",""))

            r2 = session.get("https://agents.allstate.com"+link['href'].replace("..",""))
            soup2= BeautifulSoup(r2.text,"lxml")
            st = soup2.find_all("span",{"class":"c-address-street-1"})
            st1 = soup2.find_all("span",{"class":"c-address-street-2"})
            city = soup2.find_all("span",{"class":"c-address-city"})
            state = soup2.find_all("abbr",{"class":"c-address-state"})
            zip1 = soup2.find_all("span",{"class":"c-address-postal-code"})
            phone = soup2.find_all("span",{"class":"Teaser-phoneText"})
            name = soup2.find_all("span",{"class":"Teaser-name"})
            a = soup2.find_all("a",{"class":"Teaser-link l-row Link"})
            if a != []:
                # print(a)
                for loc in range(len(st)):
                    tem_var =[]
                    store_link = "https://agents.allstate.com/"+a[loc]['href'].replace("../../","")
                    r3 = session.get(store_link)
                    soup3= BeautifulSoup(r3.text,"lxml")
                    lat = soup3.find("meta",{"itemprop":"latitude"}).attrs['content']
                    lng = soup3.find("meta",{"itemprop":"longitude"}).attrs['content']
                    day = soup3.find("div",{"class":"c-hours-details-wrapper js-hours-table"}).find_all("tr")
                    hours_of_operation =''
                    for d in day[1:]:
                        hours_of_operation = hours_of_operation + ' '+d.attrs['content']
        
                    tem_var.append("https://agents.allstate.com")
                    tem_var.append(name[loc].text.strip())
                    try:
                        new1 = st1[loc].text.strip()
                    except:
                        new1 =''
                    tem_var.append(st[loc].text.strip() + ' ' +new1)
                    tem_var.append(city[loc].text.strip())
                    tem_var.append(state[loc].text.strip())
                    tem_var.append(zip1[loc].text.strip())
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone[loc].text.strip())
                    tem_var.append("<MISSING>")
                    tem_var.append(lat)
                    tem_var.append(lng)
                    tem_var.append(hours_of_operation)
                    tem_var.append("https://agents.allstate.com/"+a[loc]['href'].replace("../../",""))
                    #print(tem_var)
                    if tem_var[2] in address123:
                        continue
                    address123.append(tem_var[2])
                    yield tem_var
                
            else:
                name1 = soup2
                tem_var =[]
                    # print(st[loc])
                name = soup2.find("div",{"class":"Hero-type"})
                st = soup2.find("span",{"class":"c-address-street-1"}).text.strip()
                try:
                    st1 = soup2.find("span",{"class":"c-address-street-2"}).text.strip()
                except:
                    st1 = ''
                city = soup2.find("span",{"class":"c-address-city"}).text.strip()
                state = soup2.find("abbr",{"class":"c-address-state"}).text.strip()
                zip1 = soup2.find("span",{"class":"c-address-postal-code"}).text.strip()
                phone = soup2.find("span",{"class":"Core-phoneText"}).text.strip()
                lat = soup2.find("meta",{"itemprop":"latitude"}).attrs['content']
                lng = soup2.find("meta",{"itemprop":"longitude"}).attrs['content']
                tem_var.append("https://agents.allstate.com")
                tem_var.append(name.text.strip())
                tem_var.append(st+' '+st1)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(lng)
                tem_var.append(hours_of_operation)
                tem_var.append("https://agents.allstate.com"+link['href'].replace("..",""))
                #print(tem_var)
                yield tem_var
    


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


