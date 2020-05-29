import csv
from sgselenium import SgSelenium
import re

driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]

    driver.get("https://1stopstores.net")

    ele=driver.find_element_by_xpath("/html/body/div[1]/table[8]/tbody/tr/td[1]/div/table[1]/tbody/tr[1]/td/div/table/tbody/tr/td/div/table/tbody/tr/td/font/table")
    trs=ele.find_elements_by_tag_name("tr")
    tds=trs[0].find_elements_by_tag_name("td")
    for td in tds:
        locs.append(td.text.strip())
    timing.append(driver.find_element_by_xpath("/html/body/div[1]/table[8]/tbody/tr/td[1]/div/table[1]/tbody/tr[1]/td/div/table/tbody/tr/td/div/table/tbody/tr/td/font/table/tbody/tr[2]/td[1]").text.replace("\n"," "))
    timing.append(driver.find_element_by_xpath("/html/body/div[1]/table[8]/tbody/tr/td[1]/div/table[1]/tbody/tr[1]/td/div/table/tbody/tr/td/div/table/tbody/tr/td/font/table/tbody/tr[2]/td[2]").text.replace("\n"," "))
    timing.append(driver.find_element_by_xpath("/html/body/div[1]/table[8]/tbody/tr/td[1]/div/table[1]/tbody/tr[1]/td/div/table/tbody/tr/td/div/table/tbody/tr/td/font/table/tbody/tr[2]/td[3]").text.replace("\n"," "))
    timing.append(driver.find_element_by_xpath("/html/body/div[1]/table[8]/tbody/tr/td[1]/div/table[1]/tbody/tr[1]/td/div/table/tbody/tr/td/div/table/tbody/tr/td/font/table/tbody/tr[2]/td[4]").text.replace("\n"," "))
    locs.append("Brookville")
    timing.append("<MISSING>")

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://1stopstores.net")
        row.append(locs[i])
        row.append("<MISSING>")
        row.append("<MISSING>")
        row.append("<MISSING>")
        row.append("<MISSING>")
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append("<INACCESSIBLE>")  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append("https://1stopstores.net")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
