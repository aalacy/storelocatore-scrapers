from bs4 import BeautifulSoup
import csv
import re
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    p = 0
    url = "https://www.qcsupply.com/amlocator/index/ajax/"
    myobj = {
        "lat": "0",
        "lng": "0",
        "radius": "6.2137119223733395",
        "product": "0",
        "category": "0",
    }
    loclist = session.post(url, headers=headers, verify=False, data=myobj).json()[
        "items"
    ]
    for loc in loclist:
        store = loc["id"]
        lat = loc["lat"]
        longt = loc["lng"]
        content = loc["popup_html"]
        soup = BeautifulSoup(content, "html.parser")
        title = soup.find("h2").text
        link = soup.find("a")["href"]
        soup = re.sub(cleanr, "\n", str(soup))
        address = (
            re.sub(pattern, "\n", str(soup))
            .strip()
            .split("Address:", 1)[1]
            .split("Description: ", 1)[0]
            .strip()
            .splitlines()
        )
        street = address[0]
        city, state = address[1].split(", ", 1)
        pcode = address[2]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = soup.find("div", {"class": "amlocator-schedule-table"}).text.strip()
        try:
            phone = soup.findAll("a", {"class": "amlocator-link"})[1].text
        except:
            phone = "<MISSING>"
        try:
            phone = phone.split("/", 1)[0]
        except:
            pass
        data.append(
            [
                "https://www.qcsupply.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
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
