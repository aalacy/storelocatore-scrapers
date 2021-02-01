from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "cookie": "__cfduid=df90dc31aaa17de95163ffa488ccd979b1610128524; _ga=GA1.2.1599148944.1610128529; _gid=GA1.2.1125442158.1610128529; _fbp=fb.1.1610128531993.19923065",
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
    url = "https://eatatthegarage.com/locations/"
    r = session.get(url, headers=headers, verify=False)

    soup = BeautifulSoup(r.text, "html.parser")

    divlist = soup.findAll("div", {"class": "location-listing-info"})
    p = 0
    for div in divlist:
        link = div.select_one('a:contains("More Info")')["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1", {"class": "title"}).text
        hours = ""
        hourlist = soup.findAll("p", {"class": "hours"})
        for hr in hourlist:
            hours = hours + hr.text + " "
        address = soup.find("address").text.strip()
        street, city, state = address.split(",")
        state, pcode = state.lstrip().split(" ", 1)
        phone = soup.find("p", {"class": "phone"}).text

        data.append(
            [
                "https://eatatthegarage.com/",
                link,
                title.replace("\n", "").replace("\u202c", "").strip(),
                street.replace("\n", "").replace("\u202c", "").strip(),
                city.replace("\n", "").replace("\u202c", "").strip(),
                state.replace("\n", "").replace("\u202c", "").strip(),
                pcode.replace("\n", "").replace("\u202c", "").strip(),
                "US",
                "<MISSING>",
                phone.replace("\n", "").replace("\u202c", "").strip(),
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours.replace("\n", "").replace("\u202c", "").strip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
