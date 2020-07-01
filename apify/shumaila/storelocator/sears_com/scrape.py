#https://www.sears.com/stores.html

from bs4 import BeautifulSoup
import csv
import string
import re, time
import requests
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
    links = []
    p = 1
    k =0
    pattern = re.compile(r'\s\s+')
    url = "https://www.sears.com/stores.html"
    page = requests.get(url)
    #page = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    mainul = soup.find('ul',{'id':'stateList'})
    statelist = mainul.findAll('a')
    for state in statelist:
        if state['href'].find('404') == -1:
            statelink = "https://www.sears.com" + state['href']
            #print(statelink)
            flag1 = True
            while flag1:
                try:
                    page1 = requests.get(statelink)
                    #page1 = session.get(statelink, headers=headers, verify=False)
                    soup1 = BeautifulSoup(page1.text, "html.parser")
                    maindiv = soup1.find('div', {'id': 'cityList'})
                    linklist = maindiv.findAll('a',{'itemprop':'url'})
                    for blinks in linklist:
                        link = blinks['href']
                        if link.find("http") == -1 and blinks.text.find("Sears Store") > -1 :
                            #print("enter")
                            link = "https://www.sears.com" + link
                            #print(link)
                            flag = True
                            while flag:
                                try:
                                    #link = 'https://www.sears.com/stores/texas/crp-chrsti/0001217.html'
                                    #page2 = requests.get(link)
                                    page2 = session.get(link, headers=headers, verify=False)
                                    time.sleep(2)
                                    if page2.url.find('closed') > -1:
                                        print('closed',link,page2.url)
                                        break
                                    else:
                                        page2 = requests.get(link)
                                        soup2 = BeautifulSoup(page2.text, "html.parser")
                                        try:
                                            title = soup2.find('h1').text
                                        except:
                                            title = soup2.find('small', {'itemprop': 'name'}).text

                                        title = re.sub(pattern, " ", title)
                                        start = title.find("#")
                                        if start != -1:
                                            start = start + 2
                                            store = title[start:len(title)]
                                        else:
                                            store = "<MISSING>"
                                        try:
                                            street = soup2.find('span',{'itemprop':'streetAddress'}).text
                                            street = street.lstrip()
                                        except:
                                            street = "<MISSING>"
                                        try:
                                            city = soup2.find('span', {'itemprop': 'addressLocality'}).text
                                            city = city.lstrip()
                                        except:
                                            city = "<MISSING>"
                                        try:
                                            state = soup2.find('span', {'itemprop': 'addressRegion'}).text
                                            state = state.lstrip()
                                        except:
                                            state = "<MISSING>"
                                        try:
                                            pcode = soup2.find('span', {'itemprop': 'postalCode'}).text
                                        except:
                                            pcode = "<MISSING>"
                                        try:
                                            phone = soup2.find('span', {'itemprop': 'telephone'}).text
                                        except:
                                            phone = "<MISSING>"
                                        try:
                                            hourd = soup2.findAll('tr',{'itemprop':'openingHoursSpecification'})
                                            hours = ""
                                            for hour in hourd:

                                                hours = hours + hour.text + " "
                                                hours = re.sub(pattern, " ", hours)
                                        except:
                                            hours = "<MISSING>"
                                        try:
                                            soup2 = str(soup2)
                                            start = soup2.find('lat =')
                                            start = soup2.find('=',start) + 2
                                            #print(start)
                                            end = soup2.find(',',start)
                                            lat = soup2[start:end]
                                            start = soup2.find('lon =')
                                            start = soup2.find('=',start) + 2
                                            end = soup2.find(',', start)
                                            longt = soup2[start:end]
                                        except:
                                            lat =  "<MISSING>"
                                            longt =  "<MISSING>"
                                        hours = hours.replace("\n"," ")
                                        hours = hours.strip()
                                        title = title.lstrip()
                                        title = title.encode('ascii', 'ignore').decode('ascii')
                                        title = title.replace('Sears','Sears ')
                                        title = title.replace('  ',' ')
                                        flag = True
                                        for i in range(0,len(data)):                                        
                                            #print(i, pcode,data[i][6])
                                            if link == data[i][1] and title == data[i][2]:
                                                #print("exist")
                                                flag = False
                                                break
                                        if flag and title.lower().find('find your next closest Store') == -1:
                                            data.append([
                                            'https://www.sears.com/',
                                            link,
                                            title,
                                            street,
                                            city,
                                            state,
                                            pcode,
                                            'US',
                                            store,
                                            phone,
                                            "<MISSING>",
                                            lat,
                                            longt,
                                            hours
                                        ])
                                            #print(k,data[k])
                                            k += 1
                                            flag = False
                                except Exception as e:
                                    print(link)
                                    print("error",e)
                                    pass

                    flag1 = False

                except Exception as e:
                    print(statelink)
                    print("error",e)
                    pass



    return data


def scrape():
    data = fetch_data()
    write_output(data)
    #5:46

scrape()

