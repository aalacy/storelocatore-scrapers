from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests


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
    data = []
    url = "https://www.nghs.com/our-locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    dep = soup.findAll("div", {"class": "wp-block-fullmedia-blocks-fm-accordion"})
    for d in dep:
        store = d.find("div", {"class": "accordion-item-header"})
        store = store.text
        data_list = d.findAll("div", {"class": "rounded-huge"})
        for loc in data_list:
            title = loc.find("div", {"class": "title"})
            title = title.text.strip()
            phone = loc.find("div", {"class": "phone mb-2"})
            if phone:
                phone = phone.text.strip()
            else:
                phone = "<MISSING>"
            address = loc.find("div", {"class": "address-line mb-2"})
            address = address.text.strip().replace(",,", ",")
            if address.split(",")[0]:
                street = address.split(",")[0]
            if address.find("Suite") != -1:
                city = address.split(",")[2]
                state = address.split(",")[3].split(" ")[1]
                zip = address.split(",")[3].split(" ")[2]
            else:
                city = address.split(",")[1]
                state = address.split(",")[2].split(" ")[1]
                zip = address.split(",")[2].split(" ")[2]
            data.append(
                [
                    "https://www.nghs.com/",
                    "https://www.nghs.com/our-locations/",
                    title,
                    street,
                    city,
                    state,
                    zip,
                    "US",
                    "<MISSING>",
                    phone,
                    store,
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                ]
            )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
