#
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time



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
    url = 'https://www.familydollar.com/locations/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    repo_list = soup.findAll("div",{'class':'itemlist'})
    for repo in repo_list:
        try:
            repo = repo.find('a')
            #print(repo.text)
            statelink = repo['href']
            page1 = requests.get(statelink)
            soup1 = BeautifulSoup(page1.text,"html.parser")
            city_list = soup1.findAll("div",{'class':'itemlist'})
            for clink in city_list:
                try:
                    clink = clink.find('a')
                    #print("city = ", clink.text)
                    clink = clink['href']

                    page2 = requests.get(clink)
                    soup2 = BeautifulSoup(page2.text, "html.parser")
                    link_list = soup2.findAll("span", {'itemprop': 'streetAddress'})
                    for link in link_list:
                       
                        try:
                            flag = True
                            m = 0
                            while m < len(data) and flag:
                                if link.text == data[m][3]:
                                    flag = False
                                    break
                                else:
                                    m += 1
                            if flag:        
                                link = link.find('a')
                                link = link['href']
                                #print(link)
                                
                                    
                                page3 = requests.get(link)
                                soup3 = BeautifulSoup(page3.text, "html.parser")
                                #print('enter')
                                title = soup3.find('meta',{'property':'og:title'})
                                title = title['content']
                                street = soup3.find('meta', {'property': 'business:contact_data:street_address'})
                                street = street['content']
                                city = soup3.find('meta', {'property': 'business:contact_data:locality'})
                                city = city['content']
                                state = soup3.find('meta', {'property': 'business:contact_data:region'})
                                state = state['content']
                                pcode = soup3.find('meta', {'property': 'business:contact_data:postal_code'})
                                pcode = pcode['content']
                                ccode = soup3.find('meta', {'property': 'business:contact_data:country_name'})
                                ccode = ccode['content']
                                phone = soup3.find('meta', {'property': 'business:contact_data:phone_number'})
                                phone = phone['content']
                                lat = soup3.find('meta', {'property': 'place:location:latitude'})
                                lat = lat['content']
                                longt = soup3.find('meta', {'property': 'place:location:longitude'})
                                longt = longt['content']
                                try:
                                    hours = soup3.find('div',{'class':'allhours'}).text
                                except:
                                    hours = "<MISSING>"
                                start = title.find("#")
                                store = title[start+1:len(title)]
                                hours  = hours.replace("\n"," ")

                                if len(hours) < 5:
                                    hours = "<MISSING>"
                                if len(phone) < 4:
                                    phone = "<MISSING>"

                                data.append([
                                        'https://www.familydollar.com/',
                                        link,
                                        title,
                                        street,
                                        city,
                                        state,
                                        pcode,
                                        ccode,
                                        store,
                                        phone,
                                        "<MISSING>",
                                        lat,
                                        longt,
                                        hours
                                    ])
                                
                        except:
                                
                            pass
                except:
                    pass
        except:
            pass

    print(len(data))
    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

