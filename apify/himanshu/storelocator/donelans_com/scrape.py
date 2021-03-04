import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("donelans_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def getDecodedPhoneNo(encoded_phone_no):
    _dict = {}
    _dict["2"] = "ABC"
    _dict["3"] = "DEF"
    _dict["4"] = "GHI"
    _dict["5"] = "JKL"
    _dict["6"] = "MNO"
    _dict["7"] = "PQRS"
    _dict["8"] = "TUV"
    _dict["9"] = "WXYZ"

    _real_phone = ""
    for _dg in encoded_phone_no:
        for key in _dict:
            if _dg in _dict[key]:
                _dg = key
        _real_phone += _dg
    return _real_phone


def fetch_data():
    return_main_object = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://api-2.freshop.com/1/stores?app_key=donelans&has_address=true&token=014d13f8f8449f5cab1c5d480d408c61"
    locations = session.get(base_url, headers=headers).json()

    for loc in locations["items"]:
        address = loc["address_1"]
        latitude = loc["latitude"]
        name = loc["name"]
        longitude = loc["longitude"]
        city = loc["city"]
        phone1 = loc["phone"]
        zip1 = loc["postal_code"]
        state = loc["state"]
        hours = loc["hours"]
        phone = phone1.replace("\n", "").split("  ")[0]
        store = loc["store_number"]
        tem_var = []
        if len(zip1) == 6 or len(zip1) == 7:
            country = "CA"
        else:
            country = "US"
        tem_var.append("https://www.donelans.com")
        tem_var.append(name.strip().replace("&#8211;", ""))
        tem_var.append(address.strip())
        tem_var.append(city.strip())
        tem_var.append(state.strip() if state.strip() else "<MISSING>")
        tem_var.append(zip1.strip())
        tem_var.append(country)
        tem_var.append(store)
        tem_var.append(phone.strip() if phone.strip() else "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(hours.replace("\n", ""))
        tem_var.append(loc["url"])
        return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
