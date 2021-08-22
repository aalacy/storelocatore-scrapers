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
    url = "https://inglotcosmetics.com/index.php?option=com_ajax&plugin=istorelocator&tmpl=component&format=json&lat=0&lng=0&maxdistance=123456&limit=123456&source=com_contactenhanced&file=&category=12"
    loclist = session.get(url, headers=headers, verify=False).json()["data"][0]["list"]
    soup = BeautifulSoup(str(loclist), "html.parser")
    divlist = soup.findAll("li")
    p = 0
    for div in divlist:
        content = json.loads(div["data-gmapping"])
        lat = content["lat"]
        longt = content["lng"]
        store = content["id"]
        ccode = div.find("span", {"class": "loc-country"}).text
        if "England" in ccode or "US" in ccode or "Can" in ccode:
            pass
        else:
            continue
        title = div.find("div", {"class": "loc-name"}).text
        street = div.find("span", {"class": "loc-address"}).text
        city = div.find("span", {"class": "loc-city"}).text
        try:
            pcode = div.find("span", {"class": "loc-postcode"}).text
        except:
            pcode = "<MISSING>"
        state = "<MISSING>"
        if "USA" in ccode:
            ccode = "US"
            state, pcode = pcode.split(" ", 1)
        elif "Canada" in ccode:
            ccode = "CA"
        elif "England" in ccode:
            ccode = "GB"
        data.append(
            [
                "https://inglotcosmetics.com/",
                "https://inglotcosmetics.com/stores",
                title.replace("\n", ""),
                street.replace("\n", ""),
                city.replace("\n", "").replace(",", ""),
                state.replace("\n", ""),
                pcode.replace("\n", "").replace(",", ""),
                ccode,
                store,
                "<MISSING>",
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
