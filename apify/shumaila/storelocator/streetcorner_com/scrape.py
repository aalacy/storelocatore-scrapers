from bs4 import BeautifulSoup
import csv
import re
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    p = 0
    url = "https://www.streetcorner.com/consumer/"
    page = session.get(url, headers=headers, verify=False)
    cleanr = re.compile("<.*?>")
    loclist = page.text.split('<a href="https://www.streetcorner.com/store/')
    for loc in loclist:
        if loc.find("!DOCTYPE html>") == -1:
            link = "https://www.streetcorner.com/store/" + loc.split('"', 1)[0]
            page = session.get(link, headers=headers, verify=False)
            try:
                coord = str(page.text).split("center: {lat:")[2]
            except:
                continue
            lat, longt = coord.split("}", 1)[0].split(", lng: ")
            soup1 = BeautifulSoup(page.text, "html.parser")
            title = soup1.find("span", {"itemprop": "name"}).text
            try:
                street = soup1.find("span", {"itemprop": "streetAddress"}).text
            except:
                street = "<MISSING>"
            try:
                city = soup1.find("span", {"itemprop": "addressLocality"}).text
            except:
                city = "<MISSING>"
            try:
                state = soup1.find("span", {"itemprop": "addressRegion"}).text
            except:
                state = "<MISSING>"
            try:
                pcode = soup1.find("span", {"itemprop": "postalCode"}).text
            except:
                pcode = "<MISSING>"
            try:
                phone = soup1.find("span", {"itemprop": "telephone"}).text
            except:
                phone = "<MISSING>"
            try:
                hours = soup1.find("span", {"itemprop": "openingHours"})
                hours = re.sub(cleanr, "\n", str(hours)).replace("\n", " ").lstrip()
                if hours == "None":
                    hours = "<MISSING>"
            except:

                hours = "<MISSING>"
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(street) < 2:
                street = "<MISSING>"
            if len(pcode) < 2:
                pcode = "<MISSING>"
            else:
                if len(pcode) == 4:
                    pcode = "0" + pcode
            if title.find("Coming Soon") == -1:
                data.append(
                    [
                        "https://www.streetcorner.com/",
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
                        lat.strip(),
                        longt,
                        hours.replace("â€“", "-"),
                    ]
                )

                p += 1
    return data


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
