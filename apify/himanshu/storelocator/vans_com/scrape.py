import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.vans.com/"
    return_main_object=[]
    addresses=[]
    search = sgzip.ClosestNSearch()
    search.initialize()
    result_coords = []
    data_len = 0
    MAX_RESULTS = 1500
    MAX_DISTANCE = 100
    coords = search.next_coord()
    while coords:
        try:

            r = session.get("https://locations.vans.com/01062013/where-to-get-it/ajax?lang=en-EN&xml_request=%3Crequest%3E%3Cappkey%3ECFCAC866-ADF8-11E3-AC4F-1340B945EC6E%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Corder%3E_distance%3C%2Forder%3E%3Csoftmatch%3E1%3C%2Fsoftmatch%3E%3Climit%3E"+str(MAX_RESULTS)+"%3C%2Flimit%3E%3Catleast%3E1%3C%2Fatleast%3E%3Csearchradius%3E"+str(MAX_DISTANCE)+"%3C%2Fsearchradius%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E"+str(search.current_zip)+"%3C%2Faddressline%3E%3Clongitude%3E"+str(coords[1])+"%3C%2Flongitude%3E%3Clatitude%3E"+str(coords[0])+"%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Cstateonly%3E1%3C%2Fstateonly%3E%3Cnobf%3E1%3C%2Fnobf%3E%3Cwhere%3E%3Ctnvn%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftnvn%3E%3Cor%3E%3Coff%3E%3Ceq%3E%3C%2Feq%3E%3C%2Foff%3E%3Cout%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fout%3E%3Caut%3E%3Ceq%3E%3C%2Feq%3E%3C%2Faut%3E%3Coffer%3E%3Ceq%3E%3C%2Feq%3E%3C%2Foffer%3E%3Cname%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fname%3E%3Ccl%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcl%3E%3Cac%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fac%3E%3Cotw%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fotw%3E%3Ckd%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fkd%3E%3Ccs%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcs%3E%3Cclassicslites%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fclassicslites%3E%3Csf%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsf%3E%3Cpr%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpr%3E%3Cca%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fca%3E%3Csb%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsb%3E%3Csn%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsn%3E%3Cm%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fm%3E%3Cmf%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fmf%3E%3Cga%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fga%3E%3Cgf%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgf%3E%3Cvl%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fvl%3E%3Cgirlsfootapp%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgirlsfootapp%3E%3Ccaliuo%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcaliuo%3E%3Ccalinord%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcalinord%3E%3Cebts%3E%3Ceq%3E%3C%2Feq%3E%3C%2Febts%3E%3Clbts%3E%3Ceq%3E%3C%2Feq%3E%3C%2Flbts%3E%3Ccabarbour%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcabarbour%3E%3Cps%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fps%3E%3Cpsnow%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpsnow%3E%3Cpro_shop%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpro_shop%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E")
        except:
            continue
        soup = BeautifulSoup(r.text,"lxml")
        data_len = len(soup.find_all('poi'))
        location = soup.find_all('poi')

        if location != []:
            # 120
            # data_len = len(r)
            for loc in location:
               # print(loc)
                if loc.find('country').text.strip() == 'US' or loc.find('country').text.strip() == 'CA':
                    name=loc.find('name').text.strip()
                    address=loc.find('address1').text.strip()
                    city=loc.find('city').text.strip()
                    state=loc.find('state').text.strip()

                    zip = loc.find('postalcode').text.strip().replace('000wa','<MISSING>')
                    if zip  == '00000':
                        zip = ''


      
                    phone=loc.find('phone').text.strip().replace('T&#xe9;l.','').replace('&#xa0;','')
                    # storeno=loc.find('sn').text.strip()

                    # if storeno == '0':
                    #     storeno = "<MISSING>"
                    country = loc.find('country').text.strip()

                    if country=="US":
                        if len(zip) != 5 and zip != '':
                            index = 5
                            char = '-'
                            zip = zip[:index] + char + zip[index + 1:]
                    
                    lat=loc.find('latitude').text
                    lng=loc.find('longitude').text
                    result_coords.append((lat, lng))
                    hour = ''
                    page_url = "https://locations.vans.com/01062013/where-to-get-it/ajax?lang=en-EN&xml_request=%3Crequest%3E%3Cappkey%3ECFCAC866-ADF8-11E3-AC4F-1340B945EC6E%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Corder%3E_distance%3C%2Forder%3E%3Csoftmatch%3E1%3C%2Fsoftmatch%3E%3Climit%3E"+str(MAX_RESULTS)+"%3C%2Flimit%3E%3Catleast%3E1%3C%2Fatleast%3E%3Csearchradius%3E"+str(MAX_DISTANCE)+"%3C%2Fsearchradius%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E"+str(search.current_zip)+"%3C%2Faddressline%3E%3Clongitude%3E"+str(coords[1])+"%3C%2Flongitude%3E%3Clatitude%3E"+str(coords[0])+"%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Cstateonly%3E1%3C%2Fstateonly%3E%3Cnobf%3E1%3C%2Fnobf%3E%3Cwhere%3E%3Ctnvn%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftnvn%3E%3Cor%3E%3Coff%3E%3Ceq%3E%3C%2Feq%3E%3C%2Foff%3E%3Cout%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fout%3E%3Caut%3E%3Ceq%3E%3C%2Feq%3E%3C%2Faut%3E%3Coffer%3E%3Ceq%3E%3C%2Feq%3E%3C%2Foffer%3E%3Cname%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fname%3E%3Ccl%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcl%3E%3Cac%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fac%3E%3Cotw%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fotw%3E%3Ckd%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fkd%3E%3Ccs%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcs%3E%3Cclassicslites%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fclassicslites%3E%3Csf%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsf%3E%3Cpr%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpr%3E%3Cca%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fca%3E%3Csb%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsb%3E%3Csn%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsn%3E%3Cm%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fm%3E%3Cmf%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fmf%3E%3Cga%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fga%3E%3Cgf%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgf%3E%3Cvl%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fvl%3E%3Cgirlsfootapp%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgirlsfootapp%3E%3Ccaliuo%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcaliuo%3E%3Ccalinord%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcalinord%3E%3Cebts%3E%3Ceq%3E%3C%2Feq%3E%3C%2Febts%3E%3Clbts%3E%3Ceq%3E%3C%2Feq%3E%3C%2Flbts%3E%3Ccabarbour%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcabarbour%3E%3Cps%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fps%3E%3Cpsnow%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpsnow%3E%3Cpro_shop%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpro_shop%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
                    #print(page_url)
                    store=[]
                    store.append(base_url)
                    store.append(name.encode('ascii', 'ignore').decode('ascii').strip() if name.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
                    store.append(address.encode('ascii', 'ignore').decode('ascii').strip() if address.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
                    store.append(city.encode('ascii', 'ignore').decode('ascii').strip() if city.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
                    store.append(state.encode('ascii', 'ignore').decode('ascii').strip() if state.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
                    store.append(zip.replace("O","0").replace('000wa','<MISSING>') if zip.replace("O","0").replace('000wa','<MISSING>') else "<MISSING>")
                    store.append(country if country else "<MISSING>")
                    store.append("<MISSING>")
                    # store.append(storeno.encode('ascii', 'ignore').decode('ascii').strip() if storeno.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
                    store.append(phone.encode('ascii', 'ignore').decode('ascii').strip() if phone.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(lat if lat else "<MISSING>")
                    store.append(lng if lng else "<MISSING>")
                    store.append(hour.encode('ascii', 'ignore').decode('ascii').strip() if hour.strip().encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
                    store.append("<MISSING>")

                    # adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
                    if address  in addresses:
                        continue
                    addresses.append(address)
                    # print('zipp == '+zip)
                    # print("data===="+str(store))
                    yield store
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        if data_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif data_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
