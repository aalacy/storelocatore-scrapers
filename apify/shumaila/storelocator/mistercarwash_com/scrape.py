import csv
from bs4 import BeautifulSoup
import json
from sgrequests import SgRequests
import re

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
    url = "https://mistercarwash.com/locations/"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("ol", {"class": "search-list"}).select("a[href*=location]")
    r = r.text.split("var markers = ")[1].split("}]")[0]
    r = r + "}]"
    loclist = json.loads(r)
    for link in linklist:
        title = link.text
        link = link["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        street = soup.find("span", {"itemprop": "streetAddress"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        state = soup.find("span", {"itemprop": "addressRegion"}).text
        try:
            state, pcode = state.strip().split(" ", 1)
        except:
            pcode = "<MISSING>"
        phone = (
            soup.find("a", {"itemprop": "telephone"})
            .text.replace("Car Wash:", "")
            .replace("\n", " ")
            .strip()
        )
        phonelist = re.findall(
            r"\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}\b", phone
        )
        for ph in phonelist:
            match = re.match(
                "\\D?(\\d{0,3}?)\\D{0,2}(\\d{3})?\\D{0,2}(\\d{3})\\D?(\\d{4})$", ph
            )
            if match:
                phone = ph
                break
        try:
            hours = (
                soup.find("div", {"class": "hours"})
                .text.replace("Car Wash: ", "")
                .strip()
            )
        except:
            hours = "<MISSING>"
        lat = longt = store = "<MISSING>"
        for loc in loclist:
            if loc["name"].strip() == title.strip():
                lat = loc["lat"]
                longt = loc["lng"]
                store = loc["loc_id"]
                break
        if "United" in state and "TN" in city:
            state = "TN"
            city = "<MISSING>"
            pcode = "<MISSING>"
        if len(phone) < 3:
            phone = "<MISSING>"
        try:
            hours = hours.split("/", 1)[0]
        except:
            pass
        if "Kennewick" in city:
            state = "WA"
        if "Buffalo Gap Rd" in pcode:
            street = "4002 Buffalo Gap Rd"
            city = "Abilene"
            state = "TX"
            pcode = "<MISSING>"
        if "Ste 100" in city and "Austin" in state:
            street = street + " " + city
            city = state
            state = "TX"
        if "Fort Hood TX" in city:
            city = "Fort Hood"
            state = "TX"
        if "Georgia" in state:
            state = "GA"
        data.append(
            [
                "https://mistercarwash.com",
                link,
                title,
                street.strip(),
                city.strip(),
                state.strip(),
                pcode.strip(),
                "US",
                store,
                phone.strip(),
                "<MISSING>",
                lat,
                longt,
                hours.strip(),
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
