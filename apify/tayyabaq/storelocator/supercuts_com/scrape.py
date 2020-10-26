import csv
import os
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re, time
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('supercuts_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

def fetch_data():
    data = []
    store_links =[]
    st=[]
    #getting the state urls
    url = 'https://www.supercuts.com/salon-directory.html'
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    store=soup.find_all('a',class_='btn btn-primary')
    for link in store:
        st.append(link['href'])
    for ln in st:
        page = session.get(ln)
        soup = BeautifulSoup(page.content, "html.parser")
        sto=soup.find_all("a")
        for li in sto:
            sr=li['href']
            if str(sr).startswith("/locations/"):
                  store_links.append(sr)
    mylist = list(dict.fromkeys(store_links))
    #logger.info(len(mylist))
    #count=1
    for u in mylist:
        ul='https://www.supercuts.com/'+u
        #logger.info(count)
        #count+=1
        try:
            pg=session.get(ul)
        except:
            logger.info("")
        else:
            soup = BeautifulSoup(pg.content, "html.parser")
            try:
                loc=soup.find("h2",class_='hidden-xs salontitle_salonlrgtxt').text
            except:
                logger.info("")
            else:
                street=soup.find("span",class_='street-address').text
                cty=soup.find("span",itemprop='addressLocality').text
                sts=soup.find("span",itemprop='addressRegion').text
                zcode=soup.find("span",itemprop='postalCode').text
                ph=soup.find("a",id='sdp-phone').text
                hrs=soup.find('div',class_='sdp-timings-right')
                hr=hrs.find_all("span",class_=['days','hours'])
                hours =""
                for h in hr:
                    hours+=h.text
                    hours+=" "
                if not hours:
                    hours="<MISSING>"
                lat=soup.find('meta',itemprop='latitude')['content']
                long=soup.find('meta',itemprop='longitude')['content']
                num=ul[-10:-5]
                num=num.replace("-","")
                if any(c.isalpha() for c in zcode):
                    ctry ='CA'
                else:
                    ctry ='US'
                if ul.startswith('https://www.supercuts.com//locations/pr/'):
                    ctry ='PR'
        cnt = False
        for i in data:
            if num == i[8]:
                cnt= True
        if cnt == False:
            data.append([
                            'https://www.supercuts.com/',
                             ul.replace(u'\xa0',''),
                             loc.replace(u'\xa0',''),
                             street.replace(u'\xa0',''),
                             cty.replace(u'\xa0',''),
                             sts.replace(u'\xa0',''),
                             zcode.replace(u'\xa0',''),
                             ctry.replace(u'\xa0',''),
                             num.replace(u'\xa0',''),
                             ph.replace(u'\xa0',''),
                             "<MISSING>",
                             lat.replace(u'\xa0',''),
                             long.replace(u'\xa0',''),
                             hours.replace(u'\xa0','')
                             ])
    return data
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
