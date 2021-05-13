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
    cleanr = re.compile(r"<[^>]+>")
    url = "https://nicknwillys.com/locations/"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "et_pb_text_inner"})
    for div in divlist:
        coord = div.find("a")["href"]
        try:
            coord = coord.split("@")[1].split("/data")[0]
            lat, longt = coord.split(",", 1)
            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"
        det = re.sub(cleanr, " ", str(div)).strip()
        title = det.split("\n", 1)[0]
        address = det.split("\n", 1)[1].split("MAP", 1)[0].replace("\n", " ").strip()
        street, state = address.split(", ", 1)
        state, pcode = state.lstrip().split(" ", 1)
        city = street.strip().split(" ")[-1]
        street = street.replace(city, "")
        phone = det.split("Phone", 1)[1].split("(", 1)[1].strip()
        phone = "(" + phone
        data.append(
            [
                "https://nicknwillys.com/",
                "https://nicknwillys.com/locations/",
                title.strip(),
                street.lstrip(),
                city.lstrip().replace(",", ""),
                state.lstrip(),
                pcode.lstrip(),
                "US",
                "<MISSING>",
                phone.strip(),
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
