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
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    # Your scraper here

    data = []

    pattern = re.compile(r'\s\s+')

    p = 0
    m =0
    miss = 0
    #url = 'https://www.waxcenter.com/locations/search-by-state'
    url = 'https://locations.waxcenter.com/'
    page = session.get(url, headers=headers, verify=False)#requests.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    maindiv = soup.find('ul',{'id':'bowse-content'})
    repo_list = maindiv.findAll("a",{'class':'ga-link'})
    print(len(repo_list))
    for repo in repo_list:
        #print("STATE",repo.text)
        statelink = repo['href']
        #print(statelink)
        page1 = session.get(statelink, headers=headers, verify=False)#requests.get(statelink)
        soup1 = BeautifulSoup(page1.text,"html.parser")
        maindiv = soup1.find('ul',{'class','map-list'})
        city_list = maindiv.findAll("div", {'class': 'map-list-item'})
        
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
                link = link.find('a',{'class','ga-link'})
                store = link['title'].replace('#','').lstrip()
                link =  link['href']
                page3 = session.get(link, headers=headers, verify=False)#requests.get(link)
                soup3 = BeautifulSoup(page3.text, "html.parser")
                #print("link",link)
                try:
                      mn = soup3.find('div',{'class':'opening-soon'}).text
                except:
                      mn = 'error'
                
                if mn.lower().find('soon') == -1:
                      title = soup3.find('span',{'class':'location-name'}).text
                      phone = soup3.find('a', {'class': 'phone'}).text
                      #hours = soup2.find('div', {'class': 'center-hours'}).text
                      script = soup3.find('script',{'type':'application/ld+json'})
                      script = str(script)
                      start = script.find('"addressRegion"')
                      start = script.find(':',start)
                      start = script.find('"', start)+1
                      end = script.find('"', start)
                      state = script[start:end]
                      start = script.find('"postalCode"')
                      start = script.find(':', start)
                      start = script.find('"', start) + 1
                      end = script.find('"', start) 
                      pcode = script[start:end]
                      start = script.find('"streetAddress"')
                      start = script.find(':', start)
                      start = script.find('"', start) + 1
                      end = script.find('"', start) 
                      street = script[start:end]
                      start = script.find('"addressLocality"')
                      start = script.find(':', start)
                      start = script.find('"', start) + 1
                      end = script.find('"', start) 
                      city = script[start:end]
                      hours = ''
                      hourlist = soup3.findAll('div',{'class':'day-hour-row'})
                      
                      
                      for hr in hourlist:
                            hr = hr.text.lstrip().replace('\n','')
                            hours =hours +  re.sub(pattern, " ", hr)+' '
                            
                            
                          
                      if len(hours) < 3:
                            hours = '<MISSING>'
                      else:
                            hours = hours.lstrip().replace('\n','').replace('am',' am ').replace('pm',' pm ')

                      
                      script = str(soup3)
                      start = script.find('"lat"')
                      if start == -1:
                            lat = '<MISSING>'
                      else:
                            start = script.find(':', start)+1                
                            end = script.find(',', start)
                            lat = script[start:end]
                      start = script.find('"lng"')
                      if start == -1:
                            longt = '<MISSING>'
                      else:
                            start = script.find(':', start)+1               
                            end = script.find(',', start)
                            longt = script[start:end]
                      
                      
                      
                      if len(phone) < 5:
                          phone = "<MISSING>"
                      if len(lat) < 4:
                          lat = "<MISSING>"
                      if len(longt) < 4:
                          longt = "<MISSING>"
                      if len(pcode) < 4:
                          pcode = "<MISSING>"
                      if len(state) < 2:
                          state = "<MISSING>"
                      if len(city) < 4:
                          city = "<MISSING>"

                     
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
                      #print(m,data[m])
                      p += 1
                      m += 1
                      
                else:
                     miss = miss + 1
            
            
                
        

    print(len(data))
    print('total =',p)
    print('mssing= ',miss)
    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

