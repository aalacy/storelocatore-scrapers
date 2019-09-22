import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.omahasteaks.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").replace('\n', '').replace('\t', '').strip()

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

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '')
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.omahasteaks.com/servlet/OnlineShopping?Dsp=408"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'cookie': "lbdc=dr; JSESSIONID=A6172EDD52BB8D94EF5385C04C8E950B; NullTestCookie=7E2E96CB7C8D171DF7F7171CAED4CB4C951130A411948C89AAD6482C5F23E1C07758082D05AA8407; REDBANNER020718=6B68441980C7E9FE86D760A102226F174CFF91E1EFDC2CBB4BB009BE08E0B2ED0A40A3F3EDBCA1CFB56530D409B9C161; STICKYBUTTON2018=59D47CFD90457E4CF036D9298EE4A944292E374E862981341BB182929F27316FA508B5B30D460EBD10BD94E8E00550F2; TSESSIONID=A6172EDD52BB8D94EF5385C04C8E950B; persistSeed=61; persistNickNames=""; storeReminder=09/21/2019; BigIPatDRforOmahaSteaks=2432900618.20480.0000; ak_bmsc=A9C7DB385D618C16E54F5B3EEAE934A7A5FE86E2151D0000F56D865DF56A7869~pludx8Di8r9fbD5Rk+qeOUMbivEB3KxGKRyee7RdJ2XzIwatXTurPK4WD5640o+EYp1O1r4Y5UvrUJC0k0gDiuEXkVq/KhKhKMmFr5oQNtAxUz7C1cv/ZX2PmsX7urMXl6yIT97vEUwbxQf9ik9PwXHDQa4p9CjoXtDcIH/26AmsrYksbZtU1sEzFNalTKfJ1GZ428wbsUMOuFbT6l1TZ63gvchGnVp+Ybu+29OFFzSmw=; gbi_sessionId=ck0twazb100003bcloz19zwtz; gbi_visitorId=ck0twazb100013bclrx4edtlg; s_cc=true; ORA_FPC=id=2013749504579945c391569065862904; WTPERSIST=; __attentive_id=8f761a2428dd483d93415188e8b8c030; __attentive_ss_referrer='ORGANIC'; AKA_A2=A; bm_mi=8DF8619B1EF9C7F992F8B55A533B0BA5~F1ag8p1gWkCwxjmRiQ0dsT11jCePk6CTiIh6c/a2bEQuNN+48COuY0WBMYrrJvKLwO7aGs1uoKNLzKbRKxh9/jXAHC5+/0T7xkaKpzYhzHAbKBo+jCqzBfi/ud/LSLeP5z06ID7yE0gNzsldS7x7pYdm3Zqn+Tt6Oc932WGcE+G+NB012UfSEQecXrGC0j6UWVG5ZYHeCV9NGjJx/OijrWkJsJn2LgJYmd+Sjwm9UfYZvHqlDX5blCo43J/2JFUd; s_ev21=%5B%5B'RZ0412'%2C'1569091089650'%5D%5D; SC_LINKS=servlet%20%7C%20AID-7935%20%7C%20DSP-408%20%7C%20SRC-RZ0412%20%7C%20ITMSUF-WZC%5E%5Efull%20list%20of%20stores%5E%5Eservlet%20%7C%20AID-7935%20%7C%20DSP-408%20%7C%20SRC-RZ0412%20%7C%20ITMSUF-WZC%20%7C%20full%20list%20of%20stores%5E%5E; s_sq=omahasteakscom%3D%2526pid%253Dservlet%252520%25257C%252520AID-7935%252520%25257C%252520DSP-408%252520%25257C%252520SRC-RZ0412%252520%25257C%252520ITMSUF-WZC%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.omahasteaks.com%25252Fservlet%25252FOnlineShopping%25253FDsp%25253D408%2526ot%253DA; persistInitParms=1569091092581%7EAID%3D7935%7ECME%3Dfalse; JCOMMAB=CB3136ED39681FA7C5FE3CD799728A5E3ED99D4C1AAE2A25DE3100C6F35BF1D5B0FF9CE691D40A6213E17CAA9088D44C96042048E779A7C162E28FBFF1B8E617; persistCart=N6Hs7TdKxuYqnifnpPM0wkzqNdnZEraXb8v19lNT61CYZJ4ZOGQ4UuZTVTHMm020; bm_sv=E95197E13581927860AB331E918D241B~Jl3zlKvd6wKMQolWZrVg/pwSZrdOBiWRViiYFlM75dLmf2fFLo+pUgr5GW6dfL0HzmKp7r5CfrnSNZ9hWqFR6sU06a7s5ZWtyweAsDZdmXS9s9AiXpCZkp8IZ3MQE3bCPvZtPZYAF8vUR3l6F0nQlX61Y7N+eJx5LWqaDBFKAO0=",
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    session = requests.Session()
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//a[@class="citylink"]/@href')
    for store_link in store_list:
        store = etree.HTML(session.get(store_link, headers=headers).text)
        details = eliminate_space(store.xpath('.//div[@style="line-height: 120%"]//text()'))
        address = ''
        phone = ''
        store_hours = ''
        for idx, de in enumerate(details):
            if 'phone' in de.lower():
                phone = validate(de.replace('Phone:', ''))
                address = ', '.join(details[idx-2:idx])
            if 'hours:' in de.lower():
                store_hours = validate(details[idx+1:])
        output = []
        output.append(base_url) # url
        output.append(validate(store.xpath('.//b[@class="body14"]')[0].xpath('.//text()'))) #location name
        address = parse_address(address)
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode          
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(phone)) #phone
        output.append("Omaha Steaks Retail Stores") #location type
        output.append("<INACCESSIBLE>") #latitude
        output.append("<INACCESSIBLE>") #longitude
        output.append(get_value(store_hours)) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
