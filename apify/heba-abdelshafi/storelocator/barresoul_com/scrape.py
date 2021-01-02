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
    url = "https://www.barresoul.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("div", {"class": "folder"}).findAll(
        "div", {"class": "collection"}
    )
    p = 0
    for link in linklist:
        flag = 0
        title = link.text
        link = "https://www.barresoul.com" + link.find("a")["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll("div", {"class": "map-block"})
        phonelist = soup.findAll("strong")
        phone = "<MISSING>"
        for ph in phonelist:

            if "(" in ph.text and ")" in ph.text and "-" in ph.text:
                phone = ph.text.replace("|", "").strip()
                break
        for div in divlist:
            content = div["data-block-json"]
            content = json.loads(content)["location"]
            if flag == 0:
                ttnow = title
                title = title.split("&")[0]
                flag = 1
            else:
                title = ttnow.split("&")[1]
            lat = content["mapLat"]
            longt = content["mapLng"]
            street = content["addressLine1"]
            city, state = content["addressLine2"].split(", ", 1)
            state, pcode = state.lstrip().split(" ", 1)
            state = state.replace(",", "")

            data.append(
                [
                    "https://www.barresoul.com/",
                    link,
                    title.strip()
                    .replace(",\n", "")
                    .replace(")", "")
                    .replace("(", "")
                    .strip(),
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
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
