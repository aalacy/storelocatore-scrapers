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
    url = "https://www.unitedoilco.com/locations?brand=united"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("table", {"class": "list-of-station"}).findAll("tr")
    p = 0
    for div in divlist:
        rowlist = div.findAll("td")
        title = rowlist[0].text
        street = rowlist[1].text
        city = rowlist[2].text
        state = rowlist[3].text
        pcode = rowlist[4].text
        link = div.find("a")["href"]
        store = link.split("=", 1)[1]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        phone = (
            soup.select_one('h1:contains("Phone")')
            .text.replace("Phone: ", "")
            .replace(" | ", "")
        )

        data.append(
            [
                "https://www.unitedoilco.com/",
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
