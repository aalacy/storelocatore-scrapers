import requests
from bs4 import BeautifulSoup
import csv
import xlsxwriter

def parse_bank_branch(branch_link, branch_text):

    branch_data = {}

    branch_data["locator_domain"] = branch_link
    branch_data["hours_of_operation"] = ""

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
                branch_data["location_type"] = "atm"
            else:
                branch_data["location_type"] = "branch"

            branch_data["location_name"] = name
        elif line.find("address1") > -1:
            branch_data["street_address"] = line.split(":")[1]
        elif line.find("city") > -1:
            branch_data["city"] = line.split(":")[1]
        elif line.find("state") > -1:
            branch_data["state"] = line.split(":")[1]
        elif line.find("postalcode") > -1:
            branch_data["zip"] = line.split(":")[1]
        elif line.find("country") > -1:
            branch_data["country_code"] = line.split(":")[1]
        elif line.find("clientkey") > -1:
            branch_data["store_number"] = line.split(":")[1]
        elif line.find("phone") > -1:
            branch_data["phone"] = line.split(":")[1]
        elif line.find("latitude") > -1:
            branch_data["latitude"] = float(line.split(":")[1].replace(',', '').strip().replace("'", ""))
        elif line.find("longitude") > -1:
            branch_data["longitude"] = float(line.split(":")[1].replace(',', '').strip().replace("'", ""))
        elif line.find("L_HRS_SUN") > -1:
            branch_data["hours_of_operation"] += "Sun: " + line.split("L_HRS_SUN:")[1]
        elif line.find("L_HRS_MON") > -1:
            branch_data["hours_of_operation"] += "Mon: " +line.split("L_HRS_MON:")[1]
        elif line.find("L_HRS_TUES") > -1:
            branch_data["hours_of_operation"] += "Tue: " + line.split("L_HRS_TUES:")[1]
        elif line.find("L_HRS_WED") > -1:
            branch_data["hours_of_operation"] += "Wed: " + line.split("L_HRS_WED:")[1]
        elif line.find("L_HRS_THUR") > -1:
            branch_data["hours_of_operation"] += "Thur: " + line.split("L_HRS_THUR:")[1]  
        elif line.find("L_HRS_FRI") > -1:
            branch_data["hours_of_operation"] += "Fri: " + line.split("L_HRS_FRI:")[1]
        elif line.find("L_HRS_SAT") > -1:
            branch_data["hours_of_operation"] += "Sat: " + line.split("L_HRS_SAT:")[1]

    return branch_data

def write_to_file(bank_branch_list):

     with open('amerisbank.csv', 'w') as csvfile:
        field_names = ["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"]

        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        for bank_branch in bank_branch_list:

            writer.writerow({"locator_domain": bank_branch["locator_domain"],
                                "location_name" : bank_branch["location_name"],
                                "street_address" : bank_branch["street_address"],
                                "city" : bank_branch["city"],
                                "state" : bank_branch["state"],
                                "zip" : bank_branch["zip"],
                                "country_code" : bank_branch["country_code"],
                                "store_number" : bank_branch["store_number"],
                                "phone" : bank_branch["phone"],
                                "location_type" : bank_branch["location_type"],
                                "latitude" : bank_branch["latitude"],
                                "longitude" : bank_branch["longitude"],
                                "hours_of_operation" : bank_branch["hours_of_operation"]
                                })

bank_branch_list = []

bank_locations_url = 'https://banks.amerisbank.com/'


for bank_state_link in BeautifulSoup(requests.get(bank_locations_url).content, 'html.parser').find_all(class_="pin-link"):

    for bank_city_link in BeautifulSoup(requests.get(bank_state_link.get('href')).content, 'html.parser').find_all(class_="pin-link"):

        for branch_link in BeautifulSoup(requests.get(bank_city_link.get('href')).content, 'html.parser').find_all(class_="action_btn"):

            soup = BeautifulSoup(requests.get(branch_link.get('href')).content, 'html.parser')

            data = parse_bank_branch(branch_link.get('href'), soup.find_all("script")[5].getText().split("\n"))

            bank_branch_list.append(data)

write_to_file(bank_branch_list)



