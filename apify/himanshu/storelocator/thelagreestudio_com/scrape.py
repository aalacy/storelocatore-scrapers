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
    url = "https://www.thelagreestudio.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("li", {"class": "menu-locations"}).findAll("a")[1:]
    p = 0
    for link in linklist:
        link = link["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find("div", {"class": "editor-content"}).text.strip()
        content = re.sub(pattern, "\n", content).splitlines()
        m = 0
        title = content[m]
        m += 2
        street = content[m]
        m += 1
        try:
            city, state = content[m].split(", ", 1)
        except:
            m += 1
            city, state = content[m].split(", ", 1)
        state, pcode = state.strip().split(" ", 1)
        m += 1
        phone = content[m]
        m += 1
        hours = ""
        for i in range(m, len(content)):
            if "day" in content[i] or " am " in content[i]:
                hours = hours + content[i] + " "
            else:
                pass
        try:
            lat, longt = (
                soup.select_one('a:contains("GET DIRECTIONS")')["href"]
                .split("@", 1)[1]
                .split("data", 1)[0]
                .split(",", 1)
            )
            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"
        if len(phone) > 13:
            phone = "<MISSING>"
        if len(hours) < 3:
            hours = "<MISSING>"
        data.append(
            [
                "https://www.thelagreestudio.com",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                hours.replace("\xa0", ""),
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
