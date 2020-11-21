from bs4 import BeautifulSoup
import csv
import re
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("valuecityfurniture_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    final_data = []
    url = "https://www.valuecityfurniture.com/store-locator/show-all-locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    StoreName = soup.findAll("strong", {"class": "sl-storename"})
    StoreAddress = soup.findAll("span", {"class": "sl-address"})
    StorePhone = soup.findAll("span", {"class": "sl-phone"})
    StoreHours = soup.findAll("div", {"class": "store-hours-table"})
    for title, address, phone, hour  in zip(StoreName, StoreAddress,StorePhone,StoreHours):    
      title = title.text
      phone = phone.text
      phone = phone.strip()
      street = address.find("span", {"itemprop": "streetAddress"}).text
      city = address.find("span", {"itemprop": "addressLocality"}).text
      state = address.find("span", {"itemprop": "addressRegion"}).text
      pcode = address.find("span", {"itemprop": "postalCode"}).text
      hour_list = hour.findAll("ul")
      hours = ""
      for temp in hour_list:
          day = temp.find("li").text
          time = temp.find("time", {"itemprop": "openingHours"}).text
          hours = hours + day + " " + time + " "

      final_data.append(
            [
                "https://www.valuecityfurniture.com/",
                "https://www.valuecityfurniture.com/store-locator/show-all-locations",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
                hours,
            ]
        )
    return final_data



def scrape():
    data = fetch_data()
    write_output(data)

scrape()
