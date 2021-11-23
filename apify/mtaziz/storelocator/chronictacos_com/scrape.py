from bs4 import BeautifulSoup
import csv
import json
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
    p = 0
    pattern = re.compile(r"\s\s+")
    urllist = [
        "https://www.chronictacos.com/us-locations",
        "https://www.chronictacos.com/canada-locations",
    ]
    for url in urllist:
        r = session.get(url, headers=headers, verify=False)

        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.select("a[href*=restaurant]")
        ccode = "US"
        if "canada" in url:
            ccode = "CA"
        for div in divlist:
            link = div["href"]
            if "japan" in div["href"]:
                continue
            if "https://www.chronictacos.com/" in link:
                pass
            else:
                link = "https://www.chronictacos.com/" + div["href"]
            if "/-" in link:
                continue
            r = session.get(link, headers=headers, verify=False)
            loc = r.text.split("<script type='application/ld+json'>", 1)[1].split(
                "</script", 1
            )[0]

            loc = re.sub(pattern, "", loc).replace("\n", " ").strip()
            loc = json.loads(loc)
            street = loc["address"]["streetAddress"]
            city = loc["address"]["addressLocality"]
            title = city
            state = loc["address"]["addressRegion"]
            pcode = loc["address"]["postalCode"]
            phone = loc["telephone"]
            lat = loc["geo"]["latitude"]
            longt = loc["geo"]["longitude"]
            hours = (
                loc["openingHours"]
                .replace("day", "day ")
                .replace("pm", "pm ")
                .replace("CLOSED", "CLOSED ")
                .strip()
            )
            if len(hours) < 3:
                hours = "<MISSING>"
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(state) < 2 or len(state.strip()) > 2:
                state = city.split(" ")[-1]
                city = city.replace(" " + state, "")
                title = city
            if (
                len(pcode) < 3
                and '<span itemprop="addressLocality">Coming Soon</span>' in r.text
            ):
                continue
            data.append(
                [
                    "https://www.chronictacos.com",
                    link,
                    title,
                    street,
                    city.strip(),
                    state,
                    pcode,
                    ccode,
                    "<MISSING>",
                    phone,
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
