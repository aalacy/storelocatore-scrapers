# Import libraries
import requests
import time
from bs4 import BeautifulSoup
import csv
import string

from sgrequests import SgRequests
session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():   
    p = 0
    data = []
    statelist = []
    url = 'https://www.homewatchcaregivers.com/locations/'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")    
    repo_list = soup.find('select', {'id': 'LocationList_HDR0_State'})
    repo_list = repo_list.findAll('option')
    for rep in repo_list:
        statelist.append(rep.text.lower())        
     
    
    for i in range(1,len(statelist)):
        statelink = 'https://www.homewatchcaregivers.com/locations/'+statelist[i]
        print('state = ',statelink)
        r1 = session.get(statelink, headers=headers, verify=False)        
        soup1 =BeautifulSoup(r1.text, "html.parser")
        divlist = soup1.find('ul', {'class': 'state-list'})        
        divlist = divlist.findAll('li')
        for div in divlist:           
            lat = div['data-latitude']
            longt = div['data-longitude']
            det = div.find('h3')
            title = det.text
            link = det.find('a')['href']
            title = title.replace('\n','')
            link = 'https://www.homewatchcaregivers.com'+link            
            r2 = session.get(link, headers=headers, verify=False)        
            soup2 =BeautifulSoup(r2.text, "html.parser")
            try:
                phone = soup2.find('span',{'itemprop':'telephone'}).text
            except:
                phone = "<MISSING>"
            try:
                street = soup2.find('span',{'itemprop':'streetAddress'}).text
                street = street.replace('\t','')
                street = street.replace('\n',' ')
                street = street.strip()

            except:
                street = "<MISSING>"
            try:
                city = soup2.find('span',{'itemprop':'addressLocality'}).text
                city = city.replace(',','')

            except:
                city = "<MISSING>"
            try:
                state = soup2.find('span',{'itemprop':'addressRegion'}).text

            except:
                state = "<MISSING>"
            try:
                pcode = soup2.find('span',{'itemprop':'postalCode'}).text

            except:
                pcode = "<MISSING>"
            try:
                hours = soup2.find('li',{'class':'item1'}).text
                hours =hours.replace('\n','')
                hours = hours.replace('Care','')
                hours = hours.strip()
                if hours.find('24-Hour') == -1:
                    hours = "<MISSING>"
            except:
                hours = "<MISSING>"

            city = city.rstrip()
            state = state.rstrip()
            data.append([
                        'https://www.homewatchcaregivers.com',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        "<MISSING>",
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
                    ])
            #print(p,data[p])
            p += 1













                
        
       
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
