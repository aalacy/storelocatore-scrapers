import csv
import re
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
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
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    data = []
    p = 0
    myobj = {
        "searchzip": "Ohio",
        "task": "search",
        "radius": "-1",
        "option": "com_mymaplocations",
        "limit": "0",
        "component": "com_mymaplocations",
        "Itemid": "264",
        "zoom": "9",
        "format": "json",
        "geo": "",
        "limitstart": "0",
        "latitude": "",
        "longitude": "",
    }
    url = "https://hymiler.com/index.php/locations"
    loclist = session.post(url, headers=headers, data=myobj, verify=False).json()[
        "features"
    ]
    for loc in loclist:
        longt = loc["geometry"]["coordinates"][0]
        lat = loc["geometry"]["coordinates"][1]
        title = loc["properties"]["name"]
        link = "https://hymiler.com" + loc["properties"]["url"]
        desc = loc["properties"]["description"]
        soup = BeautifulSoup(desc, "html.parser")
        soup = re.sub(cleanr, "\n", str(soup))
        soup = re.sub(pattern, "\n", str(soup)).strip().splitlines()
        street = soup[1]
        city, state = soup[2].split(",")
        pcode = soup[3].rstrip().split("\xa0")[-1]
        phone = soup[-1]
        store = loc["id"]

        data.append(
            [
                "https://hymiler.com",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                "MISSING>",
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
