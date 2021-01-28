import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

import usaddress

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


def fetch_data():
    base_url = "https://gpminvestments.com/store-locator/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")

    return_main_object = []

    k = soup.find_all("script", {"type": "text/javascript"})

    for i in k:
        if "var wpgmaps_localize_marker_data" in i.text:
            response_json = json.loads(
                i.text.split("var wpgmaps_localize_marker_data =")[1]
                .strip()
                .split("}}};")[0]
                + "}}}"
            )
            break

    found_poi = []
    for i in response_json["7"].keys():
        us_zip_list = re.findall(
            re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),
            " ".join(str(response_json["7"][i]["address"]).split(" ")[1:]),
        )
        tem_var = []
        state_list = re.findall(
            r"([A-Z]{2})",
            str(response_json["7"][i]["address"].replace("US", "")),
        )
        raw_address = response_json["7"][i]["address"]
        raw_address = (re.sub(" +", " ", raw_address)).strip()

        if raw_address.count(",") > 1:
            street = raw_address.split(",")[0].strip()
            city = raw_address.split(",")[1].strip()
        else:
            address = usaddress.parse(raw_address)
            street = ""
            city = ""
            for addr in address:
                if addr[1] == "PlaceName":
                    city += addr[0].replace(",", "") + " "
                elif addr[1] == "ZipCode":
                    continue
                elif addr[1] == "StateName":
                    continue
                else:
                    street += addr[0].replace(",", "") + " "

        if not city:
            if "Roan Mountain" in raw_address:
                city = "Roan Mountain"
                street = street.replace("Roan Mountain", "").strip()
            else:
                city = street.split()[-1].strip()
                street = street.replace(city, "").strip()

        if "(" in city:
            street = street + " " + city.split()[0].strip()
            city = city.split()[-1].strip()

        if street in found_poi:
            continue
        found_poi.append(street)

        lat = response_json["7"][i]["lat"]
        lng = response_json["7"][i]["lng"]

        if str(lat) == "0":
            lat = "<MISSING>"
            lng = "<MISSING>"

        if us_zip_list:
            zip1 = us_zip_list[-1]
        else:
            zip1 = "<MISSING>"

        if state_list:
            state = state_list[-1]
        else:
            state = "<MISSING>"
        tem_var.append("https://ezmart.com")
        tem_var.append(response_json["7"][i]["title"])
        tem_var.append(street)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append(i)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append("<MISSING>")
        tem_var.append("https://gpminvestments.com/store-locator/")
        return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
