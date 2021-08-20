import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    locator_domain = "http://tapoutfitness.com/"
    ext = "locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    hrefs = base.find_all(class_="icon-monitor")

    link_list = []
    for h in hrefs:
        link = "https:" + h["href"]

        if "dhaka" in link:
            continue
        if "facebook" in link:
            continue
        if "centrito" in link:
            continue

        link_list.append(link)

    all_store_data = []
    for link in link_list:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        cont = list(base.find(class_="medium").stripped_strings)
        if "JAKARTA" in cont[1].upper():
            break

        if "COMING SOON TO" in base.find(class_="vc_column-inner").h4.text.upper():
            continue

        start_idx = link.find("//")
        end_idx = link.find(".")
        location_name = link[start_idx + 2 : end_idx]

        street_address = cont[0]
        if "," in cont[1]:
            city, state, zip_code = addy_ext(cont[1])
            hours = ""
            for h in cont[2:]:
                hours += h + " "
        else:
            street_address = street_address + " " + cont[1]
            city, state, zip_code = addy_ext(cont[2])
            hours = ""
            for h in cont[3:]:
                hours += h + " "

        hours = hours.strip()

        if hours == "":
            hours = "<MISSING>"

        country_code = "US"

        if state == "ON":
            country_code = "CA"
        if zip_code == "L4H":
            zip_code = "L4H 3S7"

        phone_number = base.find(class_="phone-number").text.strip()

        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "latitude" in str(script):
                break
        try:
            store = json.loads(str(script).split(">")[1].split("<")[0])
            lat = store["geo"]["latitude"]
            longit = store["geo"]["longitude"]
        except:
            lat = "<MISSING>"
            longit = "<MISSING>"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        page_url = link
        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            page_url,
        ]
        all_store_data.append(store_data)
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
