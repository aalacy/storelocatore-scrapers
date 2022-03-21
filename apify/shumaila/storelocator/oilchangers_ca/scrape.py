import csv
import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "cookie": "_ga='GA1.1.2000499983.1621085311; gcoc-location-finder-query={'lat':'51.8031249','lng':'-95.1958536'}; _ga_Z8VPGXEVP9=GS1.1.1621105581.4.1.1621105596.0",
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
    pattern = re.compile(r"\s\s+")
    url = "https://www.gcoc.ca/locations/"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=locations]")[2:]
    checklist = []
    for link in linklist:
        title = link.text
        link = link["href"]
        if link == "/locations/":
            continue
        if link in checklist:
            continue
        checklist.append(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.text.split("Store Locations")[2].split("Services", 1)[0]
        content = re.sub(pattern, "\n", content).strip().splitlines()
        hours = content[-1].replace("pm", "pm ").replace("day", "day ")
        title = content[0]
        street = content[1]
        city = content[2]
        state = content[3].replace(",", "")
        pcode = content[4]
        phone = content[6]
        lat, longt = (
            soup.select_one('a:contains("Direction")')["href"]
            .split("destination=", 1)[1]
            .split(",")
        )
        if "be closed" in hours:
            hours = "<MISSING>"
        if title.find("Coming Soon") == -1:
            data.append(
                [
                    "https://oilchangers.ca/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "CA",
                    "<MISSING>",
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
