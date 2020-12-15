from bs4 import BeautifulSoup
import csv
import re
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
    pattern = re.compile(r"\s\s+")
    url = "https://www.lifetime.life/view-all-locations.html"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=time-locations]")
    p = 0
    for link in linklist:
        if "http" in link["href"]:
            link = link["href"]
        else:
            link = "https://www.lifetime.life" + link["href"]
        if "life-time-locations.html" in link:
            continue
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").text
        link = r.url
        try:
            check = r.text.split('"comingSoon":"', 1)[1].split('"', 1)[0]
            if check != "":
                continue
        except:
            pass
        try:
            location = r.text.split('script type="application/ld+json">', 1)[1].split(
                "</script", 1
            )[0]
            location = re.sub(pattern, "\n", location).replace("\n", "")
            location = json.loads(location)
            title = location["name"]
            store = location["@id"].split("/")[-1]
            street = location["address"]["streetAddress"]
            city = location["address"]["addressLocality"]
            state = location["address"]["addressRegion"]
            pcode = location["address"]["postalCode"]
            ccode = location["address"]["addressCountry"]
            lat = location["geo"]["latitude"]
            longt = location["geo"]["longitude"]
            phone = location["telephone"]
        except:
            if title.find("Winter Park") > -1:
                address = soup.find("div", {"class": "m-t-2"}).text.strip().splitlines()
                street = address[3]
                city, state = address[4].split(", ", 1)
                state, pcode = state.split(" ", 1)
                phone = address[5]
                longt, lat = (
                    soup.find("iframe")["src"]
                    .split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d", 1)
                )
                ccode = "US"

        try:
            hourslink = soup.find("div", {"class": "hero-content"}).select_one(
                'a:contains("Club Hours")'
            )

            if hourslink.text.find("Future") > -1:
                continue
            hourslink = "https://www.lifetime.life" + hourslink["href"]
        except:
            continue
        r = session.get(hourslink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            hours = soup.find("table").text
            hours = (
                re.sub(pattern, "\n", hours)
                .replace("\n", " ")
                .replace("Hours", "")
                .replace("Day", "")
                .replace("HOURS", "")
                .strip()
            )
        except:
            hours = "<MISSING>"
        hours = hours.replace("Time ", "")
        data.append(
            [
                "https://www.lifetime.life/",
                link,
                title,
                street.strip(),
                city.strip(),
                state.strip(),
                pcode.strip(),
                ccode,
                store,
                phone.replace("\n", ""),
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
