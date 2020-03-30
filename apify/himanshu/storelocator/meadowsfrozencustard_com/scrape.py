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
    store_detail = []
    store_name = []
    return_main_object = []
    address1 = []
    page_url = 'http://meadowsfrozencustard.com/columns/'
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    
   
    
    k  = soup.find('div', {'class': 'page-content'}).find_all('div', {'class': 'col-lg-3'})
   
   
   
    for i in k:
        
        
        li = i.find('h3')
        if li ==None or li.text in "New Alexandria, PA":
            pass
        else:
            tem_var =[]
            location_name = li.text
            # print(location_name)
            address_tmp =i.find_all('p')[1]
            address1 = i.find_all('p')[1].text.strip().split(',')
            if(len(address1)==3):
                address = address1[0]
                city = address1[1]
                state_tmp = address1[2].split(' ')
                if(len(state_tmp)==3):
                    state = state_tmp[1]
                    zip = state_tmp[2]
                if(len(state_tmp)==4):
                    state = state_tmp[1]+' '+ state_tmp[2]
                    zip = state_tmp[3]
                if(len(state_tmp)==5):
                    state = state_tmp[1]+' '+ state_tmp[2]+' '+ state_tmp[3]
                    zip = state_tmp[4]        
              
                
            elif(len(address1)==1):
                address_tmp = address1[0].split(' ')
                address = address_tmp[0]+' '+address_tmp[1]+' '+address_tmp[2]+' '+address_tmp[3]
                city = address_tmp[4]
                state = address_tmp[5]
                zip = address_tmp[6]
                
            elif(len(address1)==2):
                address= address1[1]
                city_tmp = address_tmp.find_next_sibling("div").text.split(',')
                city = city_tmp[0]
                state_tmp = city_tmp[1].split(' ')
                state = state_tmp[1]
                zip = state_tmp[2]
                
            elif(len(address1)==4):
                address = address1[1]
                city = address1[2]
                state_tmp = address1[3].split(' ')
                state = state_tmp[1]
                zip =state_tmp[2]
            link = i.find('a')['href']  
            r1 = session.get(link, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            phone1 = soup1.find_all('div', {'class': 'contact-info'})
            hour1 =  soup1.find('div', {'class': 'about-location'})
            hour2 = list(hour1.stripped_strings)
           
            if(len(hour2)==4):
                hour= '<MISSING>'
            elif(len(hour2)==6 or len(hour2)==5 or len(hour2)==11 or len(hour2)==17):
                hour = '<MISSING>'
            elif(len(hour2)==7):
                hour3= hour2[1]+' '+hour2[2]
                if(len(hour3)< 50):
                    hour= hour2[1]+' '+hour2[2]+' '+hour2[3]+' '+hour2[4].split('Try')[0]
                   
                elif(len(hour3)< 200 and len(hour3)>100 ):
                    hour= hour2[1]+' '+hour2[2].split('Enjoy')[0]
                  
                else:
                    hour = '<MISSING>'
            elif(len(hour2)==9):
                hour3= hour2[1]+' '+hour2[2]
                if(len(hour3)< 50):
                    hour= hour2[1]+' '+hour2[2]+' '+hour2[3]
                else:
                    hour = '<MISSING>'    
            elif(len(hour2)==12):
                hour= hour2[1]+' '+hour2[2]+' '+hour2[3]
                # print(hour)
            elif(len(hour2)==13):
                hour= hour2[1]+' '+hour2[2]+' '+hour2[3]
            elif(len(hour2)==15):
                hour3= hour2[1]+' '+hour2[2]  
                if(len(hour3)> 320 and len(hour3)<330 ):
                    hour= hour2[1]
                else:
                    hour = '<MISSING>'
            elif(len(hour2)==18):
                hour= hour2[2]+' '+hour2[3]
            elif(len(hour2)==21):
                hour= hour2[4]               
            elif(len(hour2)==24):
                hour= hour2[2]+' '+hour2[3].split('*HOURS')[0] 
            elif(len(hour2)==28):
                hour= hour2[6]+' '+hour2[7].split(', (June,')[0]
                  
                
            # .replace('Contact InformationPhone: 908-393-2928','<MISSING>')
                
            if(len(phone1)==2):
                phone1 = soup1.find_all('div', {'class': 'contact-info'})[1].text.strip().replace('Contact Information','').replace('Phone:','').replace('Hours: 10AM – 11PM','')
                phone = phone1.replace('Address: 715 Gateway Center Blvd Grovetown GA 30813','<MISSING>').strip()
                # print(phone)
            else:
                phone = '<MISSING>'
      
       
                   
            tem_var.append('http://meadowsfrozencustard.com/')
            tem_var.append(location_name)
            tem_var.append(address)
            tem_var.append(city)
            tem_var.append(state) 
            tem_var.append(zip)
            tem_var.append('US')
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hour)
            tem_var.append(page_url)
            if "Canberra" in tem_var:
                pass
            else:
                
            

                return_main_object.append(tem_var)
                   
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
