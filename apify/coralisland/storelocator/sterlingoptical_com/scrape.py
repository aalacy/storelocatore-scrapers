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
    url = "https://www.sterlingoptical.com/locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select('a:contains("Store Details")')

    p = 0
    for div in divlist:
        link = div["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = (
            soup.find("a", {"class": "location-page-link-city"})
            .text.replace("\n", " ")
            .strip()
        )
        try:
            street = soup.find("span", {"class": "street-address"}).text
        except:
            continue
        city = soup.find("span", {"class": "locality"}).text
        state = soup.find("span", {"class": "region"}).text
        pcode = soup.find("span", {"class": "postal-code"}).text
        try:
            phone = soup.find("a", {"class": "tel"}).text.replace("Phone:", "").strip()
        except:
            if "Coming Soon!" in soup.find("span", {"class": "is-coming-soon"}):
                continue
        try:
            hours = soup.find("ul", {"class": "location-hours-list"}).text
            hours = re.sub(pattern, " ", hours).replace("\n", " ").strip()
        except:
            hours = "<MISSING>"
        data.append(
            [
                "https://www.sterlingoptical.com/",
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
