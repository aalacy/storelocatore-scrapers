from bs4 import BeautifulSoup
import csv
import re
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
    p = 0
    pattern = re.compile(r"\s\s+")
    url = "https://www.llbean.com/llb/shop/1000001703?nav=gn-"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    link_list = soup.find("div", {"id": "storeLocatorZone"}).findAll("a")
    for alink in link_list:
        if alink.text.find(":") == -1 or alink.find("Freeport") == -1:
            link = "https://www.llbean.com" + alink["href"]
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("h1").text
            phone = soup.find("li", {"class", "phone"}).text.strip()
            street = soup.find("span", {"class": "street-address"}).text
            city = soup.find("em", {"class": "locality"}).text
            state = soup.find("abbr", {"class": "region"}).text
            pcode = soup.find("em", {"class": "postal-code"}).text
            store = link.split("/")[-1]
            hours = (
                soup.find("ul", {"class": "hoursActive"}).text.replace("\n", "").strip()
            )
            hours = re.sub(pattern, " ", hours).strip()

            lat = r.text.split("var latitude", 1)[1].split("=", 1)[1].split(";", 1)[0]

            longt = (
                r.text.split("var longitude", 1)[1].split("=", 1)[1].split(";", 1)[0]
            )

            if len(hours) < 3:
                hours = "<MISSING>"
            data.append(
                [
                    "https://www.llbean.com",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "flagship, Bike, Boat & Ski, hunting and fishing",
                    lat,
                    longt,
                    hours,
                ]
            )
            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
