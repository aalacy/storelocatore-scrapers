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
    url = "https://broadwaypizza.com/locations.html"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "location-box2"})
    p = 0
    for div in divlist:
        title = div.find("h3").text
        link = "https://broadwaypizza.com/" + div.find("a")["href"]
        content = div.find("p").text
        content = re.sub(pattern, "\n", content).strip().splitlines()
        m = 0
        if len(content) == 4:
            street = content[m] + content[m + 1]
            m += 2
        elif len(content) == 3:
            street = content[m]
            m += 1
        city, state = content[m].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = content[-1]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            longt, lat = (
                soup.findAll("iframe")[-1]["src"]
                .split("!2d", 1)[1]
                .split("!2m", 1)[0]
                .split("!3d", 1)
            )

            try:
                lat = lat.split("!3m", 1)[0]
            except:
                pass
        except:
            lat = longt = "<MISSING>"
        data.append(
            [
                "https://broadwaypizza.com/",
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
                "<MISSING>",
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
