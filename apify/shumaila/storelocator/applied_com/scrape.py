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
    p = 0
    data = []
    streetlist = []
    pattern = re.compile(r"\s\s+")
    urllist = [
        "https://www.applied.com/store-finder/position?country=CA&hideDistances=true",
        "https://www.applied.com/store-finder/position?country=US&hideDistances=true",
    ]
    ccode = "US"
    for url in urllist:
        if "country=CA" in url:
            ccode = "CA"
        else:
            ccode = "US"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        storelist = soup.find("table", {"class": "store-list"}).findAll(
            "tr", {"class": "item"}
        )

        coordlist = r.text.split("data-stores= '{", 1)[1].split("}'", 1)[0].split("{")
        for div in storelist:
            tdlist = div.findAll("td")
            col1 = re.sub(pattern, "\n", tdlist[0].text).lstrip().splitlines()
            title = col1[0]
            store = col1[1].replace("(", "").replace(")", "").strip()
            phone = col1[2]
            address = re.sub(pattern, "\n", tdlist[1].text).lstrip().splitlines()
            link = "https://www.applied.com" + tdlist[0].find("a")["href"]
            street = address[0]
            try:
                city, state = address[1].split(", ", 1)
            except:
                if address[1].split(",", 1)[0] in link:
                    state = link.split(address[1].split(",", 1)[0] + ", ")[1].split(
                        " ", 1
                    )[0]
                    city = address[1].split(",", 1)[0]
            pcode = address[2]
            if title in streetlist:
                continue
            streetlist.append(title)
            lat = link.split("lat=", 1)[1].split("&", 1)[0]
            longt = link.split("long=", 1)[1]
            if "View Map" in phone:
                phone = "<MISSING>"
            lat = "<MISSING>"
            longt = "<MISSING>"
            for coord in coordlist:
                coord = coord.replace("\n", "").lstrip()
                try:
                    coord = "{" + coord.split("}", 1)[0] + "}"
                    coord = json.loads(coord)

                    if title.strip() == coord["name"]:
                        lat = coord["latitude"]
                        longt = coord["longitude"]
                        break
                except:
                    pass
            data.append(
                [
                    "https://www.applied.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    ccode,
                    store,
                    phone,
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
