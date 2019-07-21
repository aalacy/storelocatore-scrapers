import csv
import requests
from bs4 import BeautifulSoup
import xlsxwriter

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_bank_branch(branch_link, branch_text):

    branch_data = []

    locator_domain = branch_link
    hours_of_operation = ""
    location_name = None
    city = None
    state = None
    country_code = None
    
    relevant_text = False

    for line in branch_text: 
        if relevant_text == False and line.find("W2GI.collection.poi") == -1:
            continue
        elif line.find("servicetype") > -1:
            break
        else:
            relevant_text = True
        
        if line.find("name") > -1:
            name = line.split(":")[1]

            if name.find("ATM ONLY") > -1:
                location_type = "atm"
            else:
                location_type = "branch"

            location_name = name
        elif line.find("address1") > -1:
            street_address = line.split(":")[1]
        elif line.find("city") > -1:
            city = line.split(":")[1]
        elif line.find("state") > -1:
            state = line.split(":")[1]
        elif line.find("postalcode") > -1:
            zip = line.split(":")[1]
        elif line.find("country") > -1:
            country_code = line.split(":")[1]
        elif line.find("clientkey") > -1:
            store_number = line.split(":")[1]
        elif line.find("phone") > -1:
            phone = line.split(":")[1]
        elif line.find("latitude") > -1:
            latitude = float(line.split(":")[1].replace(',', '').strip().replace("'", ""))
        elif line.find("longitude") > -1:
            longitude = float(line.split(":")[1].replace(',', '').strip().replace("'", ""))
        elif line.find("L_HRS_SUN") > -1:
            hours_of_operation += "Sun: " + line.split("L_HRS_SUN:")[1]
        elif line.find("L_HRS_MON") > -1:
            hours_of_operation += "Mon: " +line.split("L_HRS_MON:")[1]
        elif line.find("L_HRS_TUES") > -1:
            hours_of_operation += "Tue: " + line.split("L_HRS_TUES:")[1]
        elif line.find("L_HRS_WED") > -1:
            hours_of_operation += "Wed: " + line.split("L_HRS_WED:")[1]
        elif line.find("L_HRS_THUR") > -1:
            hours_of_operation += "Thur: " + line.split("L_HRS_THUR:")[1]  
        elif line.find("L_HRS_FRI") > -1:
            hours_of_operation += "Fri: " + line.split("L_HRS_FRI:")[1]
        elif line.find("L_HRS_SAT") > -1:
            hours_of_operation += "Sat: " + line.split("L_HRS_SAT:")[1]

    branch_data = [locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
    return branch_data

def fetch_data():
    # Your scraper here
    bank_branch_list = []

    bank_locations_url = 'https://banks.amerisbank.com/'


    for bank_state_link in BeautifulSoup(requests.get(bank_locations_url).content, 'html.parser').find_all(class_="pin-link"):

        for bank_city_link in BeautifulSoup(requests.get(bank_state_link.get('href')).content, 'html.parser').find_all(class_="pin-link"):

            for branch_link in BeautifulSoup(requests.get(bank_city_link.get('href')).content, 'html.parser').find_all(class_="action_btn"):

                soup = BeautifulSoup(requests.get(branch_link.get('href')).content, 'html.parser')

                data = parse_bank_branch(branch_link.get('href'), soup.find_all("script")[5].getText().split("\n"))

                bank_branch_list.append(data)

    return bank_branch_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
