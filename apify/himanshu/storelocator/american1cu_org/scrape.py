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


def fetch_data():
    base_url= "https://www.american1cu.org/locations"
    r = session.get(base_url)
    address123 =[]
    soup= BeautifulSoup(r.text.replace('<div class="listbox" />','<div class="listbox" >'),"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    # soup1 = soup.find_all("script",{"type":"text/javascript"})
    script1 = soup.find_all("script",{"type":"text/javascript"})
    lat = []
    log = []
    lat1 = []
    log1 = []
    st1 = []
    main_st =[]
    
    k1 = session.get("https://www.american1cu.org/locations?search=&state=&options%5B%5D=atms&options%5B%5D=shared_branches")
    soup1= BeautifulSoup(k1.text.replace('<div class="listbox" />','<div class="listbox" >'),"lxml")
    listbox = (soup1.find_all("div",{"class":"listbox"}))
    script = soup1.find_all("script",{"type":"text/javascript"})
    for j in script:
        if "var point"  in j.text:
            ran = j.text.strip().split("var point = ")
            # print(len(ran))
            for p in range(len(ran)):
                if p != 0:
                    lat.append(re.findall(r'[-+]?\d*\.\d+',ran[p].split(");")[0])[0])
                    log.append(re.findall(r'[-+]?\d*\.\d+',ran[p].split(");")[0])[1])
    for index,i in enumerate(listbox,start=0):
        tem_var=[]
        name = (list(i.stripped_strings)[0])
        address = (list(i.stripped_strings)[2])
        city = list(i.stripped_strings)[3].split(",")[0]
        if len(list(i.stripped_strings)[3].split(",")[1].split( ))==1:
            zip1 = "<MISSING>"
        else:
            zip1 = list(i.stripped_strings)[3].split(",")[1].split( )[1]
        state = list(i.stripped_strings)[3].split(",")[1].split( )[0]
        if list(i.stripped_strings)[4:]==[]:
            hours = "<MISSING>"
        else:
            hours = " ".join(list(i.stripped_strings)[4:])
        phone  = "<MISSING>"
        # tem_var.append("https://www.american1cu.org")
        store_name.append(name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zip1.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("ATMs and Shared Branches")
        tem_var.append(lat[index])
        tem_var.append(log[index])
        tem_var.append(hours if hours else "<MISSING>" )
        store_detail.append(tem_var)
    
   
    for j in script1:
        if "var point"  in j.text:
            ran = j.text.strip().split("var point = ")
            marker = j.text.strip().split(")</b><br />")
            for p in range(len(ran)):
                if p != 0:
                    main_st.append(marker[p].split("<br />")[0])
                    lat1.append(re.findall(r'[-+]?\d*\.\d+',ran[p].split(");")[0])[0])
                    log1.append(re.findall(r'[-+]?\d*\.\d+',ran[p].split(");")[0])[1])
                    
                
           
    # del lat1
    # del log1[-1
    k = soup.find_all("div",{"class":"listbox"})
    for index,i in enumerate(k,start=0):
        tem_var=[]
        if len(list(i.stripped_strings)) != 4:
            name = list(i.stripped_strings)[0]
            st = list(i.stripped_strings)[2]
            city = list(i.stripped_strings)[3].split(',')[0]
            state = list(i.stripped_strings)[3].split(',')[1].split( )[0]
            zip1 = list(i.stripped_strings)[3].split(',')[1].split( )[1]
            time2 = list(i.stripped_strings)[-8:]
            if time2[0]=="Phone Banking:":
                del time2[0]
                del time2[0]
            hours = (" ".join(time2).replace("Jackson, MI 49201 ","").replace("M-60 Spring Arbor, MI 49283","").replace("M-60 Spring Arbor, MI 49283","").replace("(800) 247-2296 ","").replace("(800) 247-2296 ","").strip().replace(" This is not a public branch - DTE Employees and Retirees only.","").replace("Inside Country Market","").replace(" Driving Directions","").split("Phone Banking:")[-1].replace("Phone: 517-212-9447","").replace("Phone: (517) 212-9434","").replace("Home Office Drive Thru (0.1 mi) 203 S Perrine St.","").replace("Spring Arbor - Coming Soon! (8.49 mi)  ","").strip())
            v= list(i.stripped_strings)
            if v[4]=="Phone:":
                del v[4]
            phone = v[4].replace("Lobby Hours:","<MISSING>").replace("Drive-Thru Hours:","<MISSING>")
            p = list(i.stripped_strings)
            if p[4]=="Phone:":
                del p[4]
                del p[4]
          
            if p[4]=="Fax:":
                del p[4]
                del p[4]

            if p[4]=="Phone Banking:":
                del p[4]
                del p[4]
            location_type = "American 1 Credit Union Branches"
        else:
            name = list(i.stripped_strings)[0]
            st = list(i.stripped_strings)[2]
            city = list(i.stripped_strings)[3].split(',')[0]
            state = list(i.stripped_strings)[3].split(',')[1].split( )[0]
            zip1 = list(i.stripped_strings)[3].split(',')[1].split( )[1]
            hours = "<MISSING>"
            location_type = "American 1 Credit Union ATMs"
        # st1.append(st)


        store_name.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zip1.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append(location_type)
        for p in range(len(main_st)):
            if st==main_st[p]:
                tem_var.append(lat1[p])
                tem_var.append(log1[p])
        tem_var.append(hours if hours else "<MISSING>" )
        
        if len(tem_var)==13:
            del tem_var[-2]
            del tem_var[-2]
      
            # print((tem_var))
        store_detail.append(tem_var)
        

        # print(tem_var)
    for i in range(len(store_name)):
       store = list()
       store.append("http://spartannash.com")
       store.append(store_name[i])
       store.extend(store_detail[i])
       store.append("https://www.american1cu.org/location")
       if store[2] in address123:
            continue
       address123.append(store[2])
       return_main_object.append(store)
    return return_main_object
   



def scrape():
    data = fetch_data()
    write_output(data)


scrape()


