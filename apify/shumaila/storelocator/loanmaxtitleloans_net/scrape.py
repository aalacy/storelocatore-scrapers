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
    name = []
    p = 0

    url = "https://www.loanmaxtitleloans.net/SiteMap.xml"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("loc")
    for link in linklist:
        link = link.text
        if len(link.split("/")) < 5:
            continue
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        street = soup.find("span", {"itemprop": "streetAddress"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        state = soup.find("span", {"itemprop": "addressRegion"}).text
        pcode = soup.find("span", {"itemprop": "postalCode"}).text
        title = "Loanmax - " + city + ", " + state
        phone = soup.find("span", {"itemprop": "telephone"}).text
        hours = soup.find("div", {"class": "store_hours"}).text.replace("\n", " ")
        if street in name:
            continue
        name.append(street)
        data.append(
            [
                "https://www.loanmaxtitleloans.net",
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
                "<MISSING>",
                "<MISSING>",
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
