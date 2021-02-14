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
    url = "https://www.potatocornerusa.com"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split('"routes":{', 1)[1].split("}},")[0]
    r = "{" + r + "}}"
    loclist = json.loads(r)
    for loc in loclist:
        if "-locations" in loc:
            slink = "https://www.potatocornerusa.com" + loc.replace("./", "/")
            r = session.get(slink, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            linklist = soup.findAll("h6")
            for mlink in linklist:
                try:
                    link = mlink.find("a")["href"]
                except:
                    continue
                title = mlink.find("a").text
                link = "https://www.potatocornerusa.com" + link.replace("./", "/")
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    address = soup.select_one("a[href*=maps]").text
                except:
                    address = (
                        soup.text.split("Address:", 1)[1]
                        .split("Phone", 1)[0]
                        .replace("\n", ", ")
                        .strip()
                    )
                try:
                    street, city, state = address.split(",")
                except:
                    try:
                        street, temp, city, state = address.split(",")
                        street = street + " " + temp
                    except:
                        street, state = address.split(",")

                        city = street.split(" ")[-1]
                        street = street.replace(city, "")
                try:
                    state, pcode = state.strip().split(" ", 1)
                except:
                    pcode = "<MISSING>"
                phone = (
                    soup.text.split("Phone", 1)[1].split(":", 1)[1].split("\n", 1)[0]
                )
                if "N/A" in phone:
                    phone = "<MISSING>"
                data.append(
                    [
                        "https://www.potatocornerusa.com/",
                        link,
                        title.replace("\xa0", ""),
                        street.replace("\xa0", "")
                        .replace("Address:", "")
                        .lstrip()
                        .strip(),
                        city.replace("\xa0", "").strip(),
                        state.replace("\xa0", "").strip(),
                        pcode.replace("\xa0", "").strip(),
                        "US",
                        "<MISSING>",
                        phone.replace("\xa0", "").replace("\u200e", "").strip(),
                        "<MISSING>",
                        "<MISSING>",
                        "<MISSING>",
                        "<MISSING>",
                    ]
                )

                p += 1
        else:
            continue
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
