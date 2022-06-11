import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

base_url = "http://www.peachs.net"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    output_list = []

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    url = "https://peachs.net/locations/"
    session = SgRequests()
    req = session.get(url, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    store_list = base.find_all(class_="fl-col-content fl-node-content")[1:]
    for store in store_list:
        output = []
        output.append(base_url)  # url
        output.append(store.h2.text.strip())  # location name
        address = store.find_all(class_="fl-heading-text")[-2].text.split(",")
        street = address[0].split("•")[0].replace(": 7315", "7315").strip()
        city = address[0].split("•")[1].strip()
        state = address[1].split()[0].strip()
        zipcode = address[1].split()[1].strip()
        phone = store.find_all(class_="fl-heading-text")[-1].text.strip()
        store_hours = (
            base.find(class_="fl-col-content fl-node-content")
            .find_all("h2")[-1]
            .text.replace("EVERY LOCATION", "")
            .strip()
        )
        output.append(street)  # address
        output.append(city)  # city
        output.append(state)  # state
        output.append(zipcode)  # zipcode
        output.append("US")  # country code
        output.append("<MISSING>")  # store_number
        output.append(phone)  # phone
        output.append("<MISSING>")  # location type
        output.append("<MISSING>")  # latitude
        output.append("<MISSING>")  # longitude
        output.append(store_hours)  # opening hours
        output.append(url)
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
