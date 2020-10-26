import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def getDecodedPhoneNo(encoded_phone_no):
        _dict = {}
        _dict["2"] = "ABC"
        _dict["3"] = "DEF"
        _dict["4"] = "GHI"
        _dict["5"] = "JKL"
        _dict["6"] = "MNO"
        _dict["7"] = "PQRS"
        _dict["8"] = "TUV"
        _dict["9"] = "WXYZ"

        _real_phone = ""
        for _dg in encoded_phone_no:
            for key in _dict:
                if _dg in _dict[key]:
                    _dg = key
            _real_phone += _dg
        return _real_phone


    # print("phone ==== " + getDecodedPhoneNo(_phone))
def fetch_data():
    return_main_object =[]
    addressess =[]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
    base_url= "https://www.chelseagroton.com/Home/Why-Chelsea-Groton/Locations-Hours"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    href= soup.find_all("div",{"class":"mfp-hide white-popup-block"})[2:-5]
    id1 = []
    lat1= []
    lng1 =[]
    for index,i in enumerate(href):
        lat = i.find("a")['href'].split("/@")[-1]
        
        if len(i.find("a")['href'].split("/@"))==2:
            id1.append(i.attrs['id'])
            lat1.append(lat.split(",")[0])
            lng1.append(lat.split(",")[1])
       
    link = (soup.find_all("a",{"class":"LA-ui-accordion-header"}))

    for i in link:
        data1 = soup.find("div",{"id":i['href'].replace("#","")})

        latitude1 =''
        longitude1 = ''
        loc =list(data1.stripped_strings)
        if len(loc)!=35:
            tem_var =[]
            if data1.find("a",{"class":"popup-modal"}) != None:
                id2 = data1.find("a",{"class":"popup-modal"})['href'].replace("#","")
                for ii in range(len(id1)):
                    if id2 ==id1[ii]:
                        latitude1 = lat1[ii]
                        longitude1 = lng1[ii]
                 
            full_address = " ".join(loc)
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))
            zip1 = us_zip_list[-1]
            state_list = re.findall(r' ([A-Z]{2}) ', str(full_address))[-1]
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))[0]
            phone_list1 = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))[-1]
            name = i.text
            city = name.replace(" (Lending Center Only)","").replace("Center ","").replace(" Auto Bank Express","").replace(", Westside","")
            address = (" ".join(loc[1:4]).replace(state_list,"").replace(zip1,"").replace(phone_list,"").split("Address")[-1].replace("Get Directions","").strip().replace(",","").replace(city,"").replace("Groton","").replace("Mystic","").replace("Mystic","").replace("Norwich",""))
            hours = (full_address.split(phone_list1)[-1].replace("Send an email","").replace("Hours (walk-in pre-approvals welcome! No appointment needed*):","").replace("*after hour appointments are always available","").replace("•",""))
            tem_var.append("https://www.chelseagroton.com")
            tem_var.append(name.encode('ascii', 'ignore').decode('ascii').strip().replace("&#8211;",""))
            tem_var.append(address.encode('ascii', 'ignore').decode('ascii').strip())
            tem_var.append(city.replace("Norwichtown","Norwich"))
            tem_var.append(state_list.strip().encode('ascii', 'ignore').decode('ascii') if state_list.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" )
            tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone_list.encode('ascii', 'ignore').decode('ascii').strip() if phone_list.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
            tem_var.append("branch")
            tem_var.append(latitude1 if latitude1 else "<MISSING>")
            tem_var.append(longitude1 if longitude1 else "<MISSING>")
            tem_var.append(hours)
            tem_var.append("<MISSING>")
            # print(tem_var)
            return_main_object.append(tem_var)
        else:
            strong = data1.find_all("strong")
            for tage in strong:
                tem_var1 =[]
                st = tage.next_sibling.next_sibling.replace("\n","").strip().replace("New London, CT 06320","<MISSING>")
                city1= tage.next_sibling.next_sibling.next_sibling.next_sibling.replace("\n","").strip()
                if city1:
                    city = city1.split(",")[0]
                    state = city1.split(",")[1].split( )[0]
                    zip1 = city1.split(",")[1].split( )[1]
                else:
                    city = tage.next_sibling.next_sibling.replace("\n","").strip().split(",")[0]
                    state = tage.next_sibling.next_sibling.replace("\n","").strip().split(",")[1].split( )[0]
                    zip1 = tage.next_sibling.next_sibling.replace("\n","").strip().split(",")[1].split( )[1]
  
                tem_var1.append("https://www.chelseagroton.com")
                tem_var1.append(tage.text.encode('ascii', 'ignore').decode('ascii').strip().replace("&#8211;",""))
                tem_var1.append(st.encode('ascii', 'ignore').decode('ascii').strip())
                tem_var1.append(city.encode('ascii', 'ignore').decode('ascii').strip())
                tem_var1.append(state.strip().encode('ascii', 'ignore').decode('ascii') if state.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" )
                tem_var1.append(zip1.encode('ascii', 'ignore').decode('ascii').strip())
                tem_var1.append("US")
                tem_var1.append("<MISSING>")
                tem_var1.append("<MISSING>")
                tem_var1.append("ATM")
                tem_var1.append("<MISSING>")
                tem_var1.append("<MISSING>")
                tem_var1.append("<MISSING>")
                tem_var1.append("<MISSING>")
                
                # if tem_var1[2] in addressess:
                #     continue
        
                # addressess.append(tem_var1[2])
                # print(tem_var1)
                return_main_object.append(tem_var1)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


