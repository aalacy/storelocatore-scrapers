import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.cvs.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def parse_detail(store, link):    
    try:
        output = []
        output.append(base_url) # url
        output.append(link) # url
        address = eliminate_space(store.xpath('.//h1[@class="cvs-storeLoc-storeHeading"]/span//text()'))
        if len(address) > 2:
            output.append(address[0].replace('at', ''))#location name
            output.append(address[1]) #address    
            output.append(address[2]) #city
            output.append(address[3]) #state
            output.append(address[4]) #zipcode
            output.append('US') #country code
            output.append(get_value(eliminate_space(store.xpath('.//div[@class="floatLeft contact-details-wrap"]/span//text()'))[-1]).replace('Store #', '')) #store_number
            output.append(get_value(store.xpath('.//a[@class="cvs-storeLoc-tel_phone_numberDetail"]/@href')).replace('tel:', '')) #phone
            output.append("CVS pharmacy") #location type
            output.append('<INACCESSIBLE>') #latitude
            output.append('<INACCESSIBLE>') #longitude
            output.append(get_value(eliminate_space(store.xpath('.//ul[@class="cleanList phHours srSection"]//text()')))) #opening hours    
            return output
    except Exception as e:
        pdb.set_trace()

def fetch_data():
    output_list = []
    url = "https://www.cvs.com/store-locator/cvs-pharmacy-locations"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'cookie': 'adh_ps_pickup=off-p0; bbcart=on; sab_newfse=on; sab_displayads=on; dblistview=on; sab_ecdeals=on; echome_lean6=off-p0; mc_rio_locator2=on; mc_videovisit=on; pivotal_forgot_password=off-p0; pivotal_sso=off-p0; ps=on; refill_chkbox_remove=off-p0; rxhp=on; rxhp-two-step=off-p0; rxm=off-p4; rxm_phone_dob=off-p0; s2c_all_lean6=on; s2c_prodshelf=on; setcust_elastic=on; rxhp_aa1=off-p0-1572294937-home; gbi_visitorId=ck2avt8vj00013b85sqjmjcat; CVPF=CT-2; buynow=off; db-show-allrx=on; disable-app-dynamics=on; disable-sac=off; gbi_cvs_coupons=true; getcust_elastic=off-p0; ice-phr-offer=off; v3redirecton=false; mc_hl7=off; mdpguest=on; memberlite=on; pbmplaceorder=off; pbmrxhistory=on; rxlite=on; rxlitelob=off; v2-dash-redirection=on; ak_bmsc=8CC2F36EA1E659925FD96B972A738A3041783DD4CE2400009069B85D23998158~pl0RYaH1zYx5o/bFd2Qc7XD0vkbQGKwTjHAB8Gxp9vxYKucsv9sLQvGkipBaT3Ij2GNGEy6hVcZBjntUJ0l2aLyWTEP0MjHydv8S6djgCsmWVz4463kf6u/pXPP54VTpOGysZ6tqYeucTCuioOyI3gCVtngMvUM+7PP2VL7iJAAe4Hz8lzMq9+d4sc20tOEQp2DMtbCp3VkQv1Ood0fihtyO9XZw2xav6d5GgVJDeiOhY=; gbi_sessionId=ck2c2k3dg00003a7b807ocj9s; AMCVS_06660D1556E030D17F000101%40AdobeOrg=1; AMCV_06660D1556E030D17F000101%40AdobeOrg=-330454231%7CMCIDTS%7C18198%7CMCMID%7C32638069588277696382842805848157099549%7CMCAID%7CNONE%7CMCOPTOUT-1572373937s%7CNONE%7CvVersion%7C3.1.2; JSESSIONID=Kcs9VRLAORrlYB6aP1Z0sU99Z7WjKzq_sQoDE9vj.commerce_1310; bm_mi=D9DC638938A0BE882933E6E7BDB0435F~N4RTextzyG2KLK3X8KXbFvfRdVVxEwI356+p12cYHmmVE7zBS5Q2K1uv+ulO/PPQWUiheeIyD9pPBbn2dXllT7EHdkdZqLjnM1kNeR85cY1f07e3IU3rYOWBRz4Ffk1q/RByLRPrLkdAsAjDzpf7NRL2Alg2duFv0efduy+8FRDOsNjK5H4/VMZ7YFvbasiXW2aWJ5jXhWgn7YegUyum1emlOnRSUL9zLHf34Rxmt4fRc4Uzq7hlFK2TMewc8vAbSiEmA/6ogOf4IsNOd6CEPA==; current_page_name=cvs|dweb|store-locator|cvs-pharmacy-locations|STORE LOCATOR: PHARMACY LOCATIONS; previous_page_name=cvs|dweb|store-locator|store-locator-landing.jsp|STORE LOCATOR: RESULTS; previous_page_url=https://www.cvs.com/store-locator/cvs-pharmacy-locations; bm_sv=85C817F2230E7E725E792DC099B1A03F~gHJTNDWAui6MhwNpTaoQCAjoNGSkYry/WYx0NIDm0CzhHMFMQksxHAZEuxcMilhxqIzCmzKdVnmG2nGIgHsHWUpT8gs2+6x+rPcPz5lRKeCheyYM8M1jw7vTe0jRfXNbw+eOCXqm2Yd3Qug7AQkl0w==; akavpau_www_cvs_com_general=1572366971~id=738bcd39b4d3cd98ff47f04bcb733a9e; utag_main=v_id:016e1414d576002d577f1e17f0f403073001406b0086e$_sn:2$_ss:0$_st:1572368591548$_pn:4%3Bexp-session$ses_id:1572366737460%3Bexp-session',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)    
    state_list = response.xpath('//div[@class="states"]//a/@href')
    for state in state_list:
        state = base_url + state
        state_response = etree.HTML(session.get(state, headers=headers).text)
        if state_response is not None:
            city_list = eliminate_space(state_response.xpath('//div[@class="states"]//a/@href'))
            store_list = eliminate_space(state_response.xpath('//div[@class="stores-wrap"]//p[@class="directions-link"]//a/@href'))
            if len(city_list) > 0:
                for city in city_list:
                    city = base_url + city
                    city_response = etree.HTML(session.get(city, headers=headers).text)
                    if city_response is not None:
                        store_list = eliminate_space(city_response.xpath('//div[@class="stores-wrap"]//p[@class="directions-link"]//a/@href'))
                        if len(store_list) > 0:
                            for store in store_list:
                                store = base_url + store
                                store_response = etree.HTML(session.get(store, headers=headers).text)
                                if store_response is not None:
                                    output_list.append(parse_detail(store_response, store))
                        else:
                            output_list.append(parse_detail(city_response, city))
            elif len(store_list) > 0:
                for store in store_list:
                    store = base_url + store
                    store_response = etree.HTML(session.get(store, headers=headers).text)
                    if store_response is not None:
                        output_list.append(parse_detail(store_response, store))
            else:
                output_list.append(parse_detail(state_response, state))
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
