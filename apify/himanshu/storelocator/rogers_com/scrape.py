import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rogers_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(include_canadian_fsas = True)
    MAX_RESULTS = 75
    MAX_DISTANCE = 50
    # current_results_len = 0  # need to update with no of count.
    # zip_code = search.next_zip()
    coord = search.next_coord()



    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.rogers.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    # page_url = "<MISSING>"


    while coord:
        result_coords = []
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        # try:
        data = {
        'select':"Record_ID,SCID,Gplus_URL,Location_Name,Address_Or_Intersection,Address2,City,State_Or_Province,ZIP_Or_Postal_Code,Business_Phone,Fax,Intersection,IPhone_And_Access,Wireless_Phones_Access,PAYGO_Phones_Access,PAYGO_Cards,Wireless_Products_Access,Messaging_Paging_Access,Internet_Service,Cable_TV,Digital_TV,RV_Sales_Rentals,MyHome_Advantage,Cellular_Repair,Phone_Upgrades,Car_Phone_Installation,Wireless_Accepts_CC_Cheq,Wireless_Accepts_Cash,Cable_Accepts_CC_Cheq,Cable_Accepts_Cash,Pickup_Return_Dig_Equipmt,Pickup_Exch_Int_Modem,Messaging_Paging_HW_Exch,Home_Phone_Sales,Priority1,Priority2,Priority3,Priority10,Movies_And_Games_For_Rent,Hi_Def_For_Sale,Hi_Def_For_Rent,Games_For_Sale,Rogers_Portable_Internet,Rogers_Video_Store,Rogers_Plus_Store,Business_Voice_Data,Fleet_Management,Email_Solutions,Wireless_Business,Face_to_Face,Games_Trade_In,Wireless_Content_Transfer,Rocket_Stick,Netbook_wRocketMobileInt,Rocket_Hub,Rocket_Mobile_Hotspot,Ipad_Microsims,MicroSIMs,Biz_Wireless,Biz_Internet_TV,Biz_Phone,Biz_Specialist_Available,Customer_Learning_WIR,Customer_Learning_Cable,Trade_Up,Wireless_HP,SHM_Sales,SHM_Assessments,Smart_Home_Monitoring,Device_tuneup,Rogers_Credit_Cards,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday,Monday_FR,Tuesday_FR,Wednesday_FR,Thursday_FR,Friday_FR,Saturday_FR,Sunday_FR,Book_appt_url,Small_biz_centre,Closed_smb,Promo_svc1,Promo_svc2,Promo_svc3,Promo_svc4,Latitude,Longitude,CONCAT(Longitude, ',' ,Latitude) as geometry,( 6371 * acos( cos( radians("+str(x)+") ) * cos( radians(Latitude) ) * cos( radians( Longitude ) - radians( "+str(y)+") )+sin( radians("+str(x)+") ) * sin( radians( Latitude )))) AS distance",
        'where':"(Closed_smb=''AND Small_biz_centre='Y'AND ( 6371 * acos( cos( radians("+str(x)+") ) * cos( radians(Latitude) ) * cos( radians( Longitude ) - radians("+str(y)+") )+sin( radians("+str(x)+") ) * sin( radians( Latitude ))))<10)OR(Closed_smb=''AND Priority1='Y'AND ( 6371 * acos( cos( radians("+str(x)+") ) * cos( radians(Latitude) ) * cos( radians( Longitude ) - radians("+str(y)+") )+sin( radians("+str(x)+") ) * sin( radians( Latitude ))))<10)OR(Closed_smb=''AND Priority2='Y'AND ( 6371 * acos( cos( radians("+str(x)+") ) * cos( radians(Latitude) ) * cos( radians( Longitude ) - radians("+str(y)+") )+sin( radians("+str(x)+") ) * sin( radians( Latitude ))))<10)",
        "order": "distance ASC",
        "limit" : "75",
        "channelID":"ROGERS"
        }
        # logger.info("data ===" + data)
        try:
            r= session.post ('https://1-dot-rogers-store-finder.appspot.com/searchRogersStoresService',data = data,headers = headers)
        except:
            continue
        json_data = r.json()
        # except:
        #     continue
        # logger.info(json_data['features'])
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        features_len = len(json_data['features'])
        # logger.info(features_len)
        if json_data['features'] != []:
            for z in json_data['features']:
                location_name = z['properties']['LocationName'] + "-" +z['properties']['City']
                
                street_address = z['properties']['Address2'] +" " +z['properties']['Intersection']+ " "+z['properties']['AddressOrIntersection']
                page_url = "https://www.rogers.com/business/contact-us/store-locator?store="+z['properties']['SCID']
                # logger.info(page_url)
                city = z['properties']['City']

                state = z['properties']['StateOrProvince']
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(z['properties']['ZIPOrPostalCode']))
                if ca_zip_list:
                    zipp = ca_zip_list[0]
                    country_code = "CA"
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(z['properties']['ZIPOrPostalCode']))
                if us_zip_list:
                    zipp = us_zip_list[0]
                    country_code = "US"
                # logger.info(zipp)


                phone = z['properties']['Business_Phone']

                store_number = z['properties']['Record_ID']

                hours_of_operation = "Monday: " + z['properties']['Monday'] +  "    " + "Tuesday: " + z['properties']['Tuesday'] +  "   " +"Wednesday: " + z['properties']['Wednesday'] +  "  "+ "Thursday: " + z['properties']['Thursday'] +  "   "+"Friday: " + z['properties']['Friday'] +  "  "+"Saturday: " + z['properties']['Saturday'] +  "    "+"Sunday: " + z['properties']['Sunday']

                latitude = z['properties']['Latitude']

                longitude = z['properties']['Longitude']

                result_coords.append((latitude, longitude))

                if street_address in addresses:
                        continue

                addresses.append(street_address)

                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')

                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')

                # logger.info(location_name+" | "+street_address + " | " + city + " | " +state +" | "+ zipp + " | "+phone+"  | "+hours_of_operation + " | "+ latitude+" | "+ longitude +" | "+store_number)


                # logger.info("data===="+str(store))
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

                # return_main_object.append(store)
                yield store
        if features_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        if features_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        # else:
        #     raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
