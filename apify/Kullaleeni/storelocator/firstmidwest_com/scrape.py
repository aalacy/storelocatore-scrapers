from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    
    url = 'https://locations.firstmidwest.com/directory'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    state_list = soup.findAll('a', {'class': 'Directory-listLink'})
    #print("states = ",len(state_list))
    p = 0
    for states in state_list:
        states = 'https://locations.firstmidwest.com/'+states['href']

        #print(states)
        r = session.get(states, headers=headers, verify=False)  
        soup =BeautifulSoup(r.text, "html.parser")   
        branchlist = soup.findAll('a', {'class': 'Directory-listLink'})
        #print(len(branchlist))
        for branch in branchlist:
            branch = 'https://locations.firstmidwest.com/'+branch['href']
            #print(branch)
            r = session.get(branch, headers=headers, verify=False)  
            soup =BeautifulSoup(r.text, "html.parser")   
            divlist = soup.findAll('li', {'class': 'Directory-listTeaser'})
            linklist = []
            flag = 0
            if len(divlist) == 0:
                #content = soup.find('div',{'class':'core'}).text
                linklist.append(branch)
                flag =1
                #print(content)
            else:
                for div in divlist:
                    link = div.find('a',{'class':'Teaser-titleLink'})['href']
                    link = 'https://locations.firstmidwest.com/'+link.replace('../','')
                    linklist.append(link)
            for link in linklist:
                if flag == 0:
                    r = session.get(link, headers=headers, verify=False)
                    soup =BeautifulSoup(r.text, "html.parser")
                title = soup.find('title').text
                try:
                    title = title.split(':')[0]
                except:
                    pass
                content = soup.find('div',{'class':'Core'})
                street = content.find('span',{'class':'c-address-street-1'}).text
                city = content.find('span',{'class':'c-address-city'}).text
                state = content.find('span',{'class':'c-address-state'}).text
                pcode = content.find('span',{'class':'c-address-postal-code'}).text
                try:
                    phone = content.find('div',{'itemprop':'telephone'}).text
                except:
                    phone = '<MISSING>'
                try:
                    hours = content.find('table',{'class':'c-hours-details'}).text
                    hours = hours.replace('Day of the WeekHours','').replace('PM','PM ').replace('Closed','Closed ')
                    hours = hours.replace('Mon','Mon ').replace('Tue','Tue ').replace('Wed','Wed ').replace('Thu','Thu ').replace('Fri','Fri ').replace('Sat','Sat ').replace('Sun','Sun ')
                except:
                    hours = '<MISSING>'

                ltype = 'Branch'
                try:
                    if content.find('div',{'itemprop':'containsPlace'}).text.find('ATM Hours') > -1:
                        ltype = ltype + ' | ATM'
                except:
                    pass

                state =state.replace('Wisconsin','WI')
                data.append([
                        'https://www.firstmidwest.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone,
                        ltype,
                        '<MISSING>',
                        '<MISSING>',
                        hours
                    ])
                #print(p,data[p])
                p += 1
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
