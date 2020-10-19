import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "http://www.familyfoodsstores.com/locations.html"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    

    links=[]
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone = []
    hours =[]

    
    k = soup.find('table',{'border':"0","cellspacing":"0","cellpadding":"0"})
   
    k1 = (k.find_all("a")[4:][:-4])

    for i in k1:
        tem_var=[]
        link = "http://www.familyfoodsstores.com/"+i['href']
        r = session.get(link,headers=headers)
        soup1= BeautifulSoup(r.text,"lxml")
        map_link = soup1.find("a",string="Map It Now!")["href"]
        req = session.get(map_link, headers = headers)
        maps = BeautifulSoup(req.text,"lxml")
        map_link = req.url
        at_pos = map_link.rfind("@")
        latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
        longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
        if not latitude[3:5].isnumeric():
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        st2 = soup1.find("table",{"width":"950","border":"0","cellspacing":"0","cellpadding":"0"})
        k1=st2.find_all("td",{"align":"left","valign":"top"})
        k2=(list(k1[6].stripped_strings))
  
        if "View Our Weekly Ad!" in k2:
            phone  = k2[5]
        else:
            phone = k2[-1]
        st = k2[1]
        name = k2[0]
        city = k2[2].split(',')[0]
        state = k2[2].split(',')[1].split( )[0]
        zip1 = k2[2].split(',')[1].split( )[1]
        store_name.append(name.replace("\xe2\x80\x99","").replace("\x80","").encode("ascii", "replace").decode().replace("?","-"))
        links.append(link)
        tem_var.append(st.replace("Box 68","68"))
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append("<MISSING>")
        store_detail.append(tem_var)


   
  

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.familyfoodsstores.com")
        store.append(links[i])
        store.append(store_name[i])
        store.extend(store_detail[i])
     
        return_main_object.append(store) 
    return return_main_object

 

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


