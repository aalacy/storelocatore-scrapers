from bs4 import BeautifulSoup
import csv
import string
import re, time, json

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    data = []
    pattern = re.compile(r'\s\s+') 
    p = 0   
    #url = 'https://www.waxcenter.com/locations/search-by-state'
    url = 'https://locations.waxcenter.com/'
    page = session.get(url, headers=headers, verify=False)#requests.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    maindiv = soup.find('ul',{'id':'bowse-content'})
    repo_list = maindiv.findAll("a",{'class':'ga-link'})
    #print(len(repo_list))
    for repo in repo_list:
        #print("STATE",repo.text)
        statelink = repo['href']
        #print(statelink)
        page1 = session.get(statelink, headers=headers, verify=False)#requests.get(statelink)
        soup1 = BeautifulSoup(page1.text,"html.parser")
        maindiv = soup1.find('ul',{'class','map-list'})
        city_list = maindiv.findAll("div", {'class': 'map-list-item'})
        #print('city-',len(city_list))
        
        for clink in city_list:
            #link = link.find('a')
            clink = clink.find('a',{'class','ga-link'})['href']
            #print(clink)
            page2 = session.get(clink, headers=headers, verify=False)#requests.get(clink)
            soup2 = BeautifulSoup(page2.text,"html.parser")
            maindiv = soup2.find('ul',{'class','map-list'})
            link_list = maindiv.findAll("div", {'class': 'map-list-item'})            
            #print("BRANCHES",len(link_list))
            for link in link_list:
                if link.text.lower().find('soon') > -1:
                    continue
                
                link = link.find('a',{'class','ga-link'})
                store = link['title'].split('#')[1]
                title =  link.text.replace('\n','')
                link = link['href']
                #print(link)
                page3 = session.get(link, headers=headers, verify=False)#requests.get(link)               
                hours = BeautifulSoup(page3.text,'html.parser')
                try:
                    hours = hours.find('div',{'class':'hours'}).text
                    hours = re.sub(pattern,' ',hours).lstrip()
                except:
                    hours = 'Temporarily Closed'
                loc = page3.text.split('<script type="application/ld+json">',1)[1].split('[',1)[1].split('"additionalType":',1)[0]                
                loc = loc.strip() +'}'
                loc = loc.replace(',}','}')
                loc = json.loads(loc)
                lat = loc['geo']['latitude']
                longt=  loc['geo']['longitude']
                #hours = loc['openingHours']
                phone = loc['address']['telephone']
                street = loc['address']['streetAddress']
                city = loc['address']['addressLocality']
                state = loc['address']['addressRegion']
                pcode = loc['address']['postalCode']             
                       
                data.append([
                      'https://www.waxcenter.com/',
                      link,
                      title,
                      street,
                      city,
                      state,
                      pcode,
                      "US",
                      store,
                      phone,
                      "<MISSING>",
                      lat,
                      longt,
                      hours
                  ])
                #print(p,data[p])
                p += 1
                
                #input()
                 

    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

