from bs4 import BeautifulSoup
import csv
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
    url = "https://dougashy.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("ul", {"class": "sub-menu"}).findAll("li")
    maplink = "https://dougashy.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxRqlWqBQCnUQoG"
    coordlist = session.get(maplink, headers=headers, verify=False).json()["markers"]
    p = 0

    for link in linklist:
        link = link.find("a")["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll("div", {"class": "fl-rich-text"})
        for div in divlist:
            if div.text.find("Address") > -1:
                title = div.find("h2").text
                det = div.findAll("p")
                address = det[0].text.splitlines()
                street = address[1]
                state = address[2].replace(", , ", ", ")
                city, state = state.split(", ", 1)
                state = state.lstrip()
                state, pcode = state.split(" ")
                phone = div.find("a").text
                for mp in det:
                    if mp.text.find("Hours") > -1:
                        hours = (
                            mp.text.replace("\n", " ")
                            .replace("Store Hours", "")
                            .lstrip()
                        )
                lat = "<MISSING>"
                longt = "<MISSING>"
                for coord in coordlist:
                    if (
                        pcode in coord["address"]
                        and street.strip().split(" ")[0] in coord["address"]
                    ):
                        lat = coord["lat"]
                        longt = coord["lng"]
                        break
                data.append(
                    [
                        "https://dougashy.com/",
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
