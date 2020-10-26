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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 0
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.fastmed.com/urgent-care-centers/' 
    r = session.get(url, headers=headers, verify=False)
    soup =BeautifulSoup(r.text, "html.parser")   
    statelist = soup.find('div', {'class': 'states-list'})
    statelist = statelist.findAll('h2')
    for state in statelist:
        print(state.text)
        state = state.find('a')['href']
        #print(state)
        r = session.get(state, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        branchlist = soup.find('div',{'id':'all-locations'}).findAll('h3')
        #print(len(branchlist))
        for branch in branchlist:
            try:
                branch = branch.find('a')['href']
            except:
                continue
            print(branch)
            r = session.get(branch, headers=headers, verify=False)
            soup =BeautifulSoup(r.text, "html.parser")
            hours = ''
            hourd = soup.find('div',{'id':'hours'})
            hourd = hourd.find('ul')
            
            try:
               hours = re.sub(pattern, " ", str(hourd.text))
               hours = hours.replace('\n',' ').strip()            
            except Exception as e:
                print(e)
                hours = '<MISSING>'
            
            
            title = soup.find('h1').text
            title = re.sub(pattern, " ", str(title))
            street = soup.find('div',{'class':'location-street-address'}).text.splitlines()[1].lstrip()
           
            soup = str(soup)           
            start = soup.find('"addressLocality"')
            start = soup.find(':',start)
            start = soup.find('"',start)+1
            end = soup.find('"',start)
            city = soup[start:end]
            start = soup.find('"addressRegion"')
            start = soup.find(':',start)
            start = soup.find('"',start)+1
            end = soup.find('"',start)
            state = soup[start:end]
            start = soup.find('"postalCode"')
            start = soup.find(':',start)
            start = soup.find('"',start)+1
            end = soup.find('"',start)
            pcode = soup[start:end]
            start = soup.find('"telephone"')
            if start != -1:
                start = soup.find(':',start)
                start = soup.find('"',start)+1
                end = soup.find('"',start)
                phone = soup[start:end]
            else:
                phone = '<MISSING>'
            start = soup.find('"latitude"')
            start = soup.find(':',start)
            start = soup.find('"',start)+1
            end = soup.find('"',start)
            lat = soup[start:end]
            start = soup.find('"longitude"')
            start = soup.find(':',start)
            start = soup.find('"',start)+1
            end = soup.find('"',start)
            longt = soup[start:end]
            #title = title.replace('\xa0',' ')
            title = title.encode('ascii', 'replace').decode()
            title = title.replace('?','-')
            data.append(['https://www.fastmed.com/',branch, title, street, city, state, pcode, 'US', '<MISSING>', phone, '<MISSING>', lat, longt, hours])
            #print(p,data[p])
            p += 1
            #input()
            
        
    
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
