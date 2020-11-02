import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pga_com')




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
    base_url= "https://www.pga.com/play"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    addressess = []
    store_detail=[]
    return_main_object=[]

    all_state =soup.find("div",{"class":re.compile("jss176 jss367")}).find_all("a")
    for state1 in all_state:

        try:
            r1 = requests.get("https://www.pga.com"+state1['href'])
        except:
            pass

        soup1= BeautifulSoup(r1.text,"lxml")
        all_city =soup1.find("ul",{"class":re.compile("jss182 jss183")}).find_all("a")
        
        for city in all_city:
            # logger.info("city====================== ","https://www.pga.com"+city['href'])
            try:
                r2 = requests.get("https://www.pga.com"+city['href'])
            except:
                pass

            soup2= BeautifulSoup(r2.text,"lxml")
            all_store_link =soup2.find_all("a",{"data-gtm-content-type":re.compile("Facility")})
            for store1 in all_store_link:
                name = ''
                st =''
                zipp =''
                tem_var =[]
                state =''
                stopwords = "','"
                new_words = [word for word in list(store1.stripped_strings) if word not in stopwords]

                if len(new_words) == 5:
                    name = new_words[0]
                    state_list = re.findall(r'([A-Z]{2})', str(new_words[-2].strip().lstrip()))
                    # logger.info('--------------------------------------',state_list,new_words[-2].strip().lstrip())
                    if state_list:
                        state = state_list[-1]
                        # logger.info('-----------------------------------------',state)      

                    if len(new_words[1:-2])==2:
                        st = new_words[1:-2][0]
                        city = new_words[1:-2][1]

                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(new_words[-1]))
                    if us_zip_list:
                        zipp = us_zip_list[-1]

                    page_url ="https://www.pga.com"+store1['href']

                elif len(new_words) == 4:
                    name = new_words[0]
                    city = new_words[1]
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(new_words[-1].strip().lstrip()))

                    state_list = re.findall(r'([A-Z]{2})', str(new_words[-2].strip().lstrip()))
                    if state_list:
                        state = state_list[-1]

                    if us_zip_list:
                        zipp = us_zip_list[-1]

                    page_url ="https://www.pga.com"+store1['href']
                # else:
                #     logger.info("https://www.pga.com"+store1['href'])
                #     logger.info("===================== len ", len(new_words))
                    # logger.info(new_words)

                try:
                    r3 = requests.get("https://www.pga.com"+store1['href'])
                except:
                    pass

                soup3 = BeautifulSoup(r3.text,"lxml")
                all_data = list(soup3.find("div",{"class":"MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-4"}).stripped_strings)
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(all_data))

                if phone_list:
                    phone = phone_list[-1]
                else:
                    phone = ""
                
                
                tem_var.append("https://pga.com")
                tem_var.append(name if name else "<MISSING>")
                tem_var.append(st.replace("Do not use, AZ 85226","<MISSING>").replace("No Address Available","<MISSING>").strip().lstrip() if st.replace("No Address Available","<MISSING>").replace("Do not use, AZ 85226","<MISSING>").strip().lstrip() else "<MISSING>")
                tem_var.append(city.replace("Do not use","<MISSING>").strip() if  city.replace("Do not use","<MISSING>").strip() else "<MISSING>")
                tem_var.append(state if state else "<MISSING>")
                tem_var.append(zipp if zipp else "<MISSING>")
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone if phone else "<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(page_url)
                # logger.info("========================",tem_var)
                if tem_var[2] in addressess:
                    continue
                addressess.append(tem_var[2])
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                yield tem_var
                


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


