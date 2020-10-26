import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    addresses=[]
    phone =[]
    for i in range(1,58):
        new_link = "https://www.canadianjewellers.com/directory/?page="+str(i)
        r = session.get(
            "https://www.canadianjewellers.com/directory/?page="+str(i), headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        address_tmp = soup.find_all('div', {'class': 'conceal map_data'})
        phone1 =soup.find_all('div', {'class': 'directory-listing-items'})
        for p in phone1:
            phone_list = (p.find_all("a",{"href":re.compile("tel")}))
            for j in phone_list:
                phone.append(j.text)
           

        for index,j in enumerate(address_tmp):
            tem_var =[]
            st = j.attrs['data-address']
            latitude1 = j.attrs['data-lat']
            longitude1 = j.attrs['data-long']
            detail = list(j.stripped_strings)

            if  detail[-1]=="View Details":
                del detail[-1]

            state = (detail[-1].replace(" Canada","").replace("USA","").replace("Corner Brook Plaza","<MISSING>").replace("None","").replace("Ontario","ON").replace("Nova Scotia","<MISSING>").replace("Edmonton","<MISSING>"))

            # print(detail)
            if len(detail)==3:
                address = detail[1].replace("- Seattle","<MISSING>")
                name = detail[0]
            elif len(detail)==4:
                name = detail[0]
                address = detail[1]
            elif len(detail)==2:
                name = detail[0]
                address = detail[1].replace("QC","<MISSING>")
                
      
            if latitude1:
                latitude = latitude1
            else:
                latitude = "<MISSING>"
            
            if longitude1:
                longitude = longitude1
            else:
                longitude = "<MISSING>"

            tem_var.append("https://www.canadianjewellers.com")
            tem_var.append(name.replace("\x90","").replace("0xc2","").encode('ascii', 'ignore').decode('ascii').strip())
            tem_var.append(address.replace("\x90","").replace("0xc2","").encode('ascii', 'ignore').decode('ascii').strip())
            tem_var.append("<INACCESSIBLE>")
            tem_var.append(state.replace("\x90","").replace("0xc2","").encode('ascii', 'ignore').decode('ascii').strip()) 
            tem_var.append("<MISSING>")
            tem_var.append("CA")
            tem_var.append("<MISSING>")
            tem_var.append(phone[index].replace("\x90","").replace("0xc2","").encode('ascii', 'ignore').decode('ascii').strip())
            tem_var.append("<MISSING>")
            tem_var.append(latitude.replace("\x90","").replace("0xc2","").encode('ascii', 'ignore').decode('ascii').strip())
            tem_var.append(longitude.replace("\x90","").replace("0xc2","").encode('ascii', 'ignore').decode('ascii').strip())
            tem_var.append("<MISSING>")
            tem_var.append(new_link)
            
            if tem_var[2] in addresses:
                continue
        
            addresses.append(tem_var[2])
            yield tem_var
            # print("======================tem",tem_var)
            # print(tem_var)
           
           



        # print("==========================================================",new_link)
    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
