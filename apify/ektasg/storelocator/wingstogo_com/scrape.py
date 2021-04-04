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
    p = 0
    data = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://wingstogo.com/all-locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "view-more"})
    for div in divlist:
        link = "https://wingstogo.com" + div.select_one("a[href*=location]")["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find("div", {"class": "loc-details-full"})
        if "COMING SOON!" in content.text:
            continue
        title = (
            content.find("div", {"class": "loc-details-title"})
            .text.replace("\n", " ")
            .replace("\t", "")
            .strip()
        )
        city = (
            content.find("span", {"class": "detail-city"})
            .text.replace("\n", " ")
            .replace("\t", "")
            .strip()
        )
        street = (
            content.find("span", {"class": "detail-address"})
            .text.replace("\n", " ")
            .replace("\t", "")
            .strip()
        )
        phone = (
            content.find("span", {"class": "detail-phone"})
            .text.replace("\n", " ")
            .replace("\t", "")
            .strip()
        )
        hours = (
            re.sub(cleanr, "\n", str(content.find("div", {"class": "location-hours"})))
            .replace("\n", " ")
            .replace("\t", "")
            .replace("Hours:  ", "")
            .strip()
        )
        try:
            longt, lat = (
                soup.find("div", {"class": "loc-details-map"})
                .find("iframe")["src"]
                .split("!2d", 1)[1]
                .split("!2m", 1)[0]
                .split("!3d", 1)
            )
        except:
            lat = longt = "<MISSING>"
        city, state = city.strip().split(", ", 1)
        state, pcode = state.lstrip().split(" ", 1)
        data.append(
            [
                "https://wingstogo.com/",
                link,
                re.sub(pattern, " ", title),
                re.sub(pattern, " ", street),
                re.sub(pattern, " ", city),
                re.sub(pattern, " ", state),
                re.sub(pattern, " ", pcode),
                "US",
                "<MISSING>",
                re.sub(pattern, " ", phone),
                "<MISSING>",
                lat,
                longt,
                re.sub(pattern, " ", hours),
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
