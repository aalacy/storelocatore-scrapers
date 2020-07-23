import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.niftyafterfifty.com/"
    page_url = "https://www.niftyafterfifty.com/locations"
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    exists = soup.findAll('p', {'class', 'font_8'})
    return_main_object = []
    store = []
    store.append(base_url)
    store.append("FLAMINGO".capitalize())
    store.append("3041 E Flamingo Rd., Suite B")
    store.append("Las Vegas".encode('ascii', 'ignore').decode('ascii').strip())
    store.append("NV".encode('ascii', 'ignore').decode('ascii').strip())
    store.append("89121-4308")
    store.append("US")
    store.append("<MISSING>")
    store.append("(702) 473-6026".encode('ascii', 'ignore').decode('ascii').strip())
    store.append("Nifty After Fifty")
    store.append("<MISSING>")
    store.append("<MISSING>")
    store.append("Hours: Monday - Friday 7:00am - 5:00pm".encode('ascii', 'ignore').decode('ascii').strip())
    store.append(page_url)
    yield store
    for data in exists:
        flg = True
        if data.find('span'):
            if data.find('span').get('style') == "font-weight:bold;":
                if "____" in data.get_text() or "Hours:" in data.get_text() or "Nifty People" in data.get_text() or "AM" in data.get_text() or "PM" in data.get_text() or "your fitness" in data.get_text():
                    flg = False
                else:
                    flg = True
            elif data.find('span').find_next('span').find_next('span').find_next('span').get('style') == "font-weight:bold;":
                if "____" in data.get_text() or "Hours:" in data.get_text() or "Nifty People" in data.get_text() or "AM" in data.get_text() or "PM" in data.get_text()  or "your fitness" in data.get_text():
                    flg = False
                else:
                    flg = True
            else:
                flg = False
        else:
            flg = False
        if flg == True:
            location_name = data.get_text().capitalize()
            # print(location_name)
            city = location_name.replace('(fitness only)','').replace('(pt only)','').replace("Brook road","Richmond").replace("Jahnke","Richmond").replace("Robious","Richmond").replace("Corporate office","Fullerton").replace("Cheyenne","Las Vegas").replace("East","").replace("West","").replace("Dt","").replace("- n. stone","").replace("- speedway","").replace("- irvington","")       
            if "," in data.find_next('p').find_next('p').get_text().strip():
                st_address = data.find_next('p').get_text().strip() + ", " + data.find_next('p').find_next('p').get_text().strip().split(',')[0]
                street_address=" ".join(st_address.split(',')[:-1])
                # print(street_address)

                state = data.find_next('p').find_next('p').get_text().strip().split(',')[1].strip().split(' ')[0].strip()
                zip = data.find_next('p').find_next('p').get_text().strip().split(',')[1].strip().split(' ')[1].strip()
            else:
                st_address = data.find_next('p').get_text() + ", " + ' '.join(data.find_next('p').find_next('p').get_text().strip().split(' ')[:-2])
                street_address=" ".join(st_address.split(',')[:-1])


                state = data.find_next('p').find_next('p').get_text().strip().split(' ')[-2]
                zip = data.find_next('p').find_next('p').get_text().strip().split(' ')[-1]
            phone = data.find_next('p').find_next('p').find_next('p').get_text().strip()[:15]
            # hours = data.find(lambda tag: (tag.name == 'span') and "fax" in tag.text)
            hours= data.find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip()
            if "Hours" in hours:
                hours_of_operation = hours.split('Hours:')[-1].strip()
            else:
                # for h in data.find_all(lambda tag: (tag.name == 'span')):
                #     print(h)
                #     print('~~~~~~~~~~~~~~~~~~~~~~')
                h   =   data.find_next('p').find_next('p').find_next('p').find_next('p').nextSibling.nextSibling
                list_h = list(h.stripped_strings)

                if "Nifty People" in "".join(list_h):
                    list_h.remove("Nifty People® Group Ex Calendar")
                # print(street_address )
                # print(list_h)
                # print(len(list_h))
                # print('~~~~~~~~~~~~~~~~~~~')
                if "Fitness Hours:" in "".join(list_h):
                    fitness_hours = "Fitness Hours : "+data.find_next('p').find_next('p').find_next('p').find_next('p').nextSibling.nextSibling.nextSibling.nextSibling.text.strip()
                    PT_hours1 = "PT Hours : " +data.find_next('p').find_next('p').find_next('p').find_next('p').nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.text.strip()
                    PT_hours = data.find_next('p').find_next('p').find_next('p').find_next('p').nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.text.strip()
                    if "Nifty People" in PT_hours:
                        PT_hours2 = ""
                    else:
                        PT_hours2 = PT_hours

                    hours_of_operation = fitness_hours + "  "+ PT_hours1 +"  "+ PT_hours2
                elif "16405 Whittier Blvd." in street_address:
                    # print(list_h)
                    h1 =  data.find_next('p').find_next('p').find_next('p').find_next('p').nextSibling.nextSibling.text.strip()
                    h2 = data.find_next('p').find_next('p').find_next('p').find_next('p').nextSibling.nextSibling.nextSibling.nextSibling.text.strip()
                    h3 = data.find_next('p').find_next('p').find_next('p').find_next('p').nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.text.strip()
                    hours = h1 + "  "+h2 + "  "+h3
                    hours_of_operation = ' '.join(hours.split()).replace('Hours:','').strip()
                elif "1801 H Street" in street_address or "23595 Moulton Parkway" in street_address or "380 W. Central Avenue" in street_address:
                    hours = data.find_next('p').find_next('p').find_next('p').find_next('p').nextSibling.nextSibling.text.strip() + ","+data.find_next('p').find_next('p').find_next('p').find_next('p').nextSibling.nextSibling.nextSibling.nextSibling.text.strip()
                    hours_of_operation = ' '.join(hours.split()).replace('Hours:','').replace('Nifty People® Group Ex Calendar','').strip()
                    # print(hours_of_operation)
                elif "\u200b"  == "".join(list_h) or "_______" in "".join(list_h) or list_h == []:
                    hours_of_operation = "<MISSING>"
                else:
                    hours_of_operation = data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip().split('Nifty')[0].strip()

            # location_name= 'FLAMINGO'
            store = []
            store.append(base_url)
            store.append(location_name.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(street_address.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(state.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Nifty After Fifty")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(page_url)
            if "92831-5205" in zip:
                continue
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
