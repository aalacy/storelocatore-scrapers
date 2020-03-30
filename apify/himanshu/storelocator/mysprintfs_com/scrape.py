from bs4 import BeautifulSoup
from sgrequests import SgRequests
import csv
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.proxy import Proxy,ProxyType
import time
import re #for regular expression


session = SgRequests()

hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation","page_url"]
# opts=Options()
# opts.add_argument('disable-infobars')
# opts.add_argument("user-agent="+"sara")
# opts.add_argument("ignore-certificate-errors")
#capabilities = webdriver.DesiredCapabilities.CHROME
#driver=webdriver.Chrome('C:\\Users\\Lenovo\\Desktop\\chrome-driver\\chromedriver',options=opts,desired_capabilities=capabilities)
url = "https://mysprintfs.com/locations"


time.sleep(3)
html = session.get(url)
soup = BeautifulSoup(html.text,"html.parser")
all_rec = soup.find_all("div",attrs={"class":"all-results"})
main_url = "https://mysprintfs.com"
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for g in all_rec:
        st = g.find_all(name="div",attrs={"class":"results"})
        for record in st:
            locator_domain="https://mysprintfs.com/"
            location_name=""
            street_address=""
            city=""
            zip_code=""
            country_code=""
            store_number=""
            contact_number=""
            location_type=""
            latitude=""
            langitude=""
            hours_of_operation=""
            state=""
            loc = record.find("a")
            urll=""
            for x in loc:
                store_number = x[:10]
                ct = x.split(",")
                if ct == []:
                    city="<MISSING>"
                else:
                    city=ct[0][10:]
                if ct == "" or len(ct)==1:
                    city="<MISSING>"
                    
                if x[-2:] == "SC":
                    state="SC"
                elif x[-2:] == "GA":
                    state="GA"
                else:
                    state="<MISSING>"
                urll = loc["href"]
            urll = main_url + urll
            # print(url1)
            adrs = record.find(name="p",attrs={"class":"addr"})
            page_url = "https://mysprintfs.com"+record.find("h5").find("a")['href']
            # print(page_url)

            html1 = session.get(page_url)
            soup1 = BeautifulSoup(html1.text,"html.parser")
            data = soup1.find(name="div", attrs={"class":"location-text"})
            location_name1 = (data.find("h1").text)
            script = soup1.find(lambda tag: (tag.name == "script") and "center" in tag.text).text.split(".maps.LatLng")[-1].split(");")[0]
            latitude = script.replace("( ",'').split(",")[0]
            longitude = script.replace("( ",'').split(",")[-1]
            # print(script.replace("( ",'').split(",")[-1])

            for ad in adrs:
                street_address = ad
                zip_code = ad[-6:]
            #data for record Store #Store #722 Louisville, GA202/204 Hwy 1 N Bypass, 30834
            #was wrong , so i am adding one condioitn here
            if "202/204 Hwy" in street_address:
                state= "GA"
            street_address = street_address.replace(",","'")
            city = city.replace(",","'")
            state = state.replace(",","'")
            extended_html = session.get(urll)
            dt = BeautifulSoup(extended_html.text,"html.parser")
            location = dt.find_all(name="div", attrs={"class":"location-button"})
            for lloc in location:
                cnt = lloc.find("a")
                contact_number = cnt.text
            contact_number = contact_number.replace(".","-")
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(street_address))

            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            


            street_address1 = street_address.replace(zipp,'').replace("'",'')
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~ ",street_address)
            data=[locator_domain,location_name1,street_address1,city,state,zip_code,"US",store_number.replace("Store #",""),contact_number,"<MISSING>",
                  latitude,longitude,"<MISSING>",page_url]
            # print(data)
            fl_writer.writerow(data)
            
