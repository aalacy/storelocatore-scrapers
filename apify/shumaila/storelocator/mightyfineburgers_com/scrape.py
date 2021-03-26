from bs4 import BeautifulSoup
import csv
import json

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
    url = "https://www.mightyfineburgers.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("a", {"class": "image-slide-anchor"})
    p = 0
    for div in divlist:

        try:
            link = "https://www.mightyfineburgers.com" + div["href"]
        except:
            continue
        if "feedback" in link:
            continue
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        content = r.text.split('data-block-json="', 1)[1].split(';"', 1)[0]
        content = (
            content.replace("&#123;", "{")
            .replace("&quot;", '"')
            .replace("&#125", "}")
            .replace("};,", "},")
            .replace(";}", "}")
        )
        content = json.loads(content)
        content = content["location"]
        title = content["addressTitle"].replace("&amp;", "&")
        street = content["addressLine1"]
        city, state = content["addressLine2"].split(",", 1)
        state, pcode = state.split(" ", 1)
        lat = content["markerLat"]
        longt = content["markerLng"]
        hours, phone = soup.text.split("Monday", 1)[1].split("\n", 1)[0].split("(")
        hours = "Monday " + hours.replace("PM", "PM ")
        phone = "(" + phone

        data.append(
            [
                "https://www.mightyfineburgers.com/",
                link,
                title,
                street,
                city.replace(",", ""),
                state.replace(",", ""),
                pcode.replace(",", ""),
                "US",
                "<MISSING>",
                phone.replace("\xa0", ""),
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
