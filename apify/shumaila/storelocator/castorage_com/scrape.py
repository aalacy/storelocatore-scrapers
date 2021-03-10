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
    url = "https://www.castorage.com/storage"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    states = soup.find("ul", {"id": "state-list"}).findAll("li")
    for s in states:
        sub_url = "https://www.castorage.com" + s.find("a").get("href")
        r = session.get(sub_url, headers=headers, verify=False)
        sub = BeautifulSoup(r.text, "html.parser")
        store = sub.findAll("div", {"class": "facility-card"})
        for loc in store:
            title = loc.find("p", {"class": "facility-name"}).text.strip()

            phone = loc.find("p", {"class": "facility-phone"}).text
            if phone:
                phone = phone.strip()
            else:
                phone = "<MISSING>"
            address = loc.find("p", {"class": "facility-address"}).text.strip()
            street = address.split("\n")[0]
            city = address.split("\n")[1].split(",")[0].strip()
            state = address.split("\n")[1].split(", ")[1].split(" ")[0]
            zip = address.split("\n")[1].split(", ")[1].split(" ")[1]
            data.append(
                [
                    "https://www.castorage.com",
                    sub_url,
                    title,
                    street,
                    city,
                    state,
                    zip,
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
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
