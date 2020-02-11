import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import json

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.childrensplace.com/'
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }



    US_HEADER = {'Host': 'www.childrensplace.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'langId': '-1',
    'storeId': '10151',
    'Pragma': 'no-cache',
    'Expires': '0',
    'catalogId': '10551',
    'deviceType': 'desktop',
    'Cache-Control': 'no-store, must-revalidate, max-age=0',
    'tcp-trace-request-id': 'CLIENT_1_1579539453928',
    'tcp-trace-session-id': 'not-found',
    'country': 'united states',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://www.childrensplace.com/us/stores',
    'Cookie': 'iShippingCookie=US|en_US|USD|1.0|1.0; _abck=0615D603AC31E8B1FB6F29C0B511CF5C~0~YAAQXKL3vfGOwnNuAQAALGfukANxJxq1en//DLp6F/qD0K5fjQAxRkuuW5+UIOmYcNaYeJjfOKbr1mwpZWfYpF0WkZJzQXYQHYKhOhqbW9cXn6bh+FSH34DBekLrx2WZVKjdMf68vhF8c7jPMpI/m0mdcygV5ZWfXzN+bjXCoa45tv7szZ3QAtZ2tJ20asrkBeJipO22D4ePbrZ0ZwAR2TX2nL7O4qtMH3mGZgYK88550edCXCqgepixfAiCnMxAmo43/Eg8r+PHIXgOG0vjHiqu0rq6XxRRJK2CXHZ1ChchDye7+2wMbgueuOz4bGOcOrUNypOz5mCijwmq9dM5~-1~-1~-1; AMCV_9A0A1C8B5329646E0A490D4D%40AdobeOrg=-1303530583%7CMCIDTS%7C18282%7CMCMID%7C63789061121685626706424227121909719311%7CMCAID%7CNONE%7CMCOPTOUT-1579545386s%7CNONE%7CvVersion%7C3.3.0; candid_userid=35571146-0456-46de-a6d2-89ea874fb15f; myPlaceAcctNbr=""; _caid=44a04349-104a-4d47-b53f-561539ce3adb; raygun4js-userid=0bc14334-234a-d20d-7ff0-24575b194ca1; QuantumMetricUserID=b428502acb6c766c9d06a46f056a0126; s_ecid=MCMID%7C63789061121685626706424227121909719311; s_pers=%20s_tbm180%3D1%7C1594244409003%3B%20v43%3D%255B%255B%2527Direct%2527%252C%25271578684542471%2527%255D%252C%255B%2527Other%252520Natural%252520Referrers%2527%252C%25271578690609007%2527%255D%255D%7C1736543409007%3B%20v28%3Dgl%253Acompanyinfo%253Acompanyinfo%7C1579541121877%3B%20v14%3D1579539353818-Repeat%7C1582131353818%3B; unbxd.userId=uid-1578684542539-2098; extole_access_token=G7BP9OGC86HSEJ87255N3T7OMM; tcpCountryDetail=MX; tcpState=DIF; ak_bmsc=DF0E3A00BB59A3799F0FDB4765B7EFBABDF7A4D56823000007D7255E7308B86F~pl2M1ML83tdHZNW9SKmi8iyJ2J8NoGn6zVczDqwY8H5u2TVopv6Ho4P8wDi6XRfUumnjAcCGeu9sowEBompYA8jNji9Lavkz594B2v9AJDQkIOsJbZp840AeXqrnESKqqvyY1gc9q5XQm0aGC1BJMbIMrrD2snekHLAIeBoVtymkVKXmnN/HDcsQPFjVtzlmEWhXc1VeLlxV3fJ3RyD+rOWppUcw3mQ1d/hMLuaGKlApPkEaDs5Z66/v7fgcAXFVx0; bm_sz=FCD1E08250BBBF852FB841FBBAE329C5~YAAQ1aT3vQAjpohvAQAAAPbPwwYtEmmDZw+1UX5LSSsBKxLgI6bnhsQh0DgS8UybF2z3Q61oUzYeQm1mI2rf0dnBtnkNYYhE5De14io07djgD6T2gs7hxlypPgVZVnsUqTrkKZ/kDXsu1hJq2clmBmuWd97D2sgyKjG65TXmMhplrYBbyTeg6f8OTpeQOvLDV4dkvkwZ92U=; check=true; mbox=session#edf1ec92a4f94e0e81dca199351f9b8e#1579540047; AMCVS_9A0A1C8B5329646E0A490D4D%40AdobeOrg=1; bm_sv=8225D9C47EEB8853B79EF00B2F0F89E8~3z+91RNti7mJKeuvXgoI1ltgC4clOmQMsxQifBuCSk/CD5Xl+zTo2Xc/8UVtbmW4SvOMhZhYM4SeJ8nkOZ0RQjdZPqYSWh/TwN5mKwBMWTxSBA5Q0dblCiP5wMX7ZmXvbj6+9/eMt83Yt+k8j33x/JmYD66ODNmpA+JRehvGF/Y=; cartItemsCount=0; WC_ACTIVEPOINTER=-1%2C10151; JSESSIONID=0000NujAXuGnqMykNHrayvD_Ofv:19ivrv5s9; pv=4; tcp_session_active=true; BIGipServer~TCP-RD1~apipool1_8443=rd1o00000000000000000000ffff0a24d6a0o8443; _cavisit=16fc3d0194b|; s_sess=%20s_cmdl%3D1%3B%20s_cc%3Dtrue%3B; unbxd.visit=repeat; unbxd.visitId=visitId-1579538194115-90895; BIGipServer~TCP-RD1~nodepool1_8443=rd1o00000000000000000000ffff0a24d69fo8443; s_sq=%5B%5BB%5D%5D',
    'TE': 'Trailers'}

    CAN_HEADER = {'Host': 'www.childrensplace.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'langId': '-1',
    'storeId': '10151',
    'Pragma': 'no-cache',
    'Expires': '0',
    'catalogId': '10551',
    'deviceType': 'desktop',
    'Cache-Control': 'no-store, must-revalidate, max-age=0',
    'tcp-trace-request-id': 'CLIENT_1_1579539453928',
    'tcp-trace-session-id': 'not-found',
    'country': 'canada',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://www.childrensplace.com/us/stores',
    'Cookie': 'iShippingCookie=US|en_US|USD|1.0|1.0; _abck=0615D603AC31E8B1FB6F29C0B511CF5C~0~YAAQXKL3vfGOwnNuAQAALGfukANxJxq1en//DLp6F/qD0K5fjQAxRkuuW5+UIOmYcNaYeJjfOKbr1mwpZWfYpF0WkZJzQXYQHYKhOhqbW9cXn6bh+FSH34DBekLrx2WZVKjdMf68vhF8c7jPMpI/m0mdcygV5ZWfXzN+bjXCoa45tv7szZ3QAtZ2tJ20asrkBeJipO22D4ePbrZ0ZwAR2TX2nL7O4qtMH3mGZgYK88550edCXCqgepixfAiCnMxAmo43/Eg8r+PHIXgOG0vjHiqu0rq6XxRRJK2CXHZ1ChchDye7+2wMbgueuOz4bGOcOrUNypOz5mCijwmq9dM5~-1~-1~-1; AMCV_9A0A1C8B5329646E0A490D4D%40AdobeOrg=-1303530583%7CMCIDTS%7C18282%7CMCMID%7C63789061121685626706424227121909719311%7CMCAID%7CNONE%7CMCOPTOUT-1579545386s%7CNONE%7CvVersion%7C3.3.0; candid_userid=35571146-0456-46de-a6d2-89ea874fb15f; myPlaceAcctNbr=""; _caid=44a04349-104a-4d47-b53f-561539ce3adb; raygun4js-userid=0bc14334-234a-d20d-7ff0-24575b194ca1; QuantumMetricUserID=b428502acb6c766c9d06a46f056a0126; s_ecid=MCMID%7C63789061121685626706424227121909719311; s_pers=%20s_tbm180%3D1%7C1594244409003%3B%20v43%3D%255B%255B%2527Direct%2527%252C%25271578684542471%2527%255D%252C%255B%2527Other%252520Natural%252520Referrers%2527%252C%25271578690609007%2527%255D%255D%7C1736543409007%3B%20v28%3Dgl%253Acompanyinfo%253Acompanyinfo%7C1579541121877%3B%20v14%3D1579539353818-Repeat%7C1582131353818%3B; unbxd.userId=uid-1578684542539-2098; extole_access_token=G7BP9OGC86HSEJ87255N3T7OMM; tcpCountryDetail=MX; tcpState=DIF; ak_bmsc=DF0E3A00BB59A3799F0FDB4765B7EFBABDF7A4D56823000007D7255E7308B86F~pl2M1ML83tdHZNW9SKmi8iyJ2J8NoGn6zVczDqwY8H5u2TVopv6Ho4P8wDi6XRfUumnjAcCGeu9sowEBompYA8jNji9Lavkz594B2v9AJDQkIOsJbZp840AeXqrnESKqqvyY1gc9q5XQm0aGC1BJMbIMrrD2snekHLAIeBoVtymkVKXmnN/HDcsQPFjVtzlmEWhXc1VeLlxV3fJ3RyD+rOWppUcw3mQ1d/hMLuaGKlApPkEaDs5Z66/v7fgcAXFVx0; bm_sz=FCD1E08250BBBF852FB841FBBAE329C5~YAAQ1aT3vQAjpohvAQAAAPbPwwYtEmmDZw+1UX5LSSsBKxLgI6bnhsQh0DgS8UybF2z3Q61oUzYeQm1mI2rf0dnBtnkNYYhE5De14io07djgD6T2gs7hxlypPgVZVnsUqTrkKZ/kDXsu1hJq2clmBmuWd97D2sgyKjG65TXmMhplrYBbyTeg6f8OTpeQOvLDV4dkvkwZ92U=; check=true; mbox=session#edf1ec92a4f94e0e81dca199351f9b8e#1579540047; AMCVS_9A0A1C8B5329646E0A490D4D%40AdobeOrg=1; bm_sv=8225D9C47EEB8853B79EF00B2F0F89E8~3z+91RNti7mJKeuvXgoI1ltgC4clOmQMsxQifBuCSk/CD5Xl+zTo2Xc/8UVtbmW4SvOMhZhYM4SeJ8nkOZ0RQjdZPqYSWh/TwN5mKwBMWTxSBA5Q0dblCiP5wMX7ZmXvbj6+9/eMt83Yt+k8j33x/JmYD66ODNmpA+JRehvGF/Y=; cartItemsCount=0; WC_ACTIVEPOINTER=-1%2C10151; JSESSIONID=0000NujAXuGnqMykNHrayvD_Ofv:19ivrv5s9; pv=4; tcp_session_active=true; BIGipServer~TCP-RD1~apipool1_8443=rd1o00000000000000000000ffff0a24d6a0o8443; _cavisit=16fc3d0194b|; s_sess=%20s_cmdl%3D1%3B%20s_cc%3Dtrue%3B; unbxd.visit=repeat; unbxd.visitId=visitId-1579538194115-90895; BIGipServer~TCP-RD1~nodepool1_8443=rd1o00000000000000000000ffff0a24d69fo8443; s_sq=%5B%5BB%5D%5D',
    'TE': 'Trailers'}

    HEADS = [US_HEADER, CAN_HEADER]
    link_list = []
    for h in HEADS:

        r = session.get('https://www.childrensplace.com/api/v2/store/getStoreLocationByCountry', headers = h)
        json_data = json.loads(r.content)
        
        base_url = 'https://www.childrensplace.com/us/store/'
       
        for loc in json_data['PhysicalStore']:

            loc_name = loc['Description'][0]['displayStoreName'].replace(' ', '').strip()

            street_address = loc['addressLine'][0]
 
            street_address = street_address.strip()
            city = loc['city'].strip()
            state = loc['stateOrProvinceName'].strip()
            zip_code = loc['postalCode'].strip()
            country_code = loc['country'].strip()
            phone_number = loc['telephone1'].strip()
            location_type = loc['addressLine'][-1]
            
            if 'PLACE' in location_type:
                location_type = 'Retail'
            elif 'OUTLET' in location_type:
                location_type = 'Outlet'
            else:
                location_type = location_type

         
            store_number = loc['uniqueID'].strip()
            link = base_url + loc_name + '-' + loc['stateOrProvinceName'].lower() + '-' + loc['city'] + '-' + loc['postalCode'].strip() + '-' + loc['uniqueID'].strip()
            link_list.append([link, [street_address, city, state, zip_code, country_code, phone_number, location_type, store_number]])
            


    

    all_store_data = []

    
    for i, link in enumerate(link_list):

        try:
            r = session.get(link[0], headers = HEADERS)
        except:
            time.sleep(10)
            r = session.get(link[0], headers = HEADERS)


        soup = BeautifulSoup(r.content, 'html.parser')
        location_name = soup.find('h2', {'itemprop': 'name'}).text
        
        street_address = link[1][0]
        city = link[1][1]
        state = link[1][2]
        zip_code = link[1][3]
        country_code = link[1][4] 


        phone_number = link[1][5]
        location_type = link[1][6]

        store_number = link[1][7]
        
        
        if 'CLOSED' in soup.find('div', {'class': 'regular-time-schedules'}).text:
            continue
        hours = ''
        
        days = soup.find_all('li', {'class': 'day-and-time-item-container'})
        for d in days:
            day_name = d.find('span', {'class': 'day-name-container'}).text
            if day_name in hours:
                break
            day_hours = d.find('span', {'class': 'hoursRange'}).text
                
            hours += day_name + ' ' + day_hours + ' '
            
        hours = hours.strip()
        
        lat = '<MISSING>'
        longit = '<MISSING>'

        location_type = '<MISSING>'
        page_url = link[0]
        print(page_url)
      
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        


    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
