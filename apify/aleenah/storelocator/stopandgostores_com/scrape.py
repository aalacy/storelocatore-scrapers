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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.stopandgostores.com/locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find_all("a", string="Store Profile ") + soup.find_all(
        "a", string="Store Profile"
    )
    p = 0
    for link in linklist:
        link = link["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        div = soup.find("div", {"class": "c3"})
        div = re.sub(cleanr, " ", str(div)).split("}")[-1].replace("\xa0", " ").strip()
        div = re.sub(pattern, "\n", str(div)).lstrip().splitlines()
        i = 0
        street = div[i]
        if len(street) < 3:
            i += 1
            street = div[i]
        i += 1
        city, state = div[i].split(", ", 1)
        i += 1
        state, pcode = state.lstrip().split(" ", 1)
        phone = div[i].replace("Phone", "").lstrip()
        title = soup.find("h6").text.strip()

        store = title.split("#", 1)[1].split("(")[0].strip()
        if street == "":
            street = city
        street = street.replace("( In& Out)", "")
        if phone.find("--") > -1 or "X" in phone or len(phone) < 10:
            phone = "<MISSING>"
        data.append(
            [
                "https://www.stopandgostores.com/",
                link,
                title,
                street.replace("\xa0", "").replace("S t", "St"),
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
            ]
        )

        p += 1

    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
