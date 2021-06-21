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
    data = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://snbconnect.com/Locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("table", {"class": "Table-Staff-3Column"}).findAll("td")
    p = 0
    for state in statelist:
        link = state.find("a", {"class": "Button2"})["href"]
        state = state.find("h2").text

        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("table", {"class": "Expandable"})

        try:

            for i in range(0, len(loclist)):

                title = loclist[i].find("h4").text
                loc = str(
                    loclist[i]
                    .find("table", {"class": "Table-Staff-2Column"})
                    .find("td")
                )

                loc = re.sub(cleanr, "\n", loc)
                loc1 = re.sub(pattern, "\n", loc).strip()
                loc = loc1.splitlines()
                street = loc[0]
                city, state = loc[1].split(", ", 1)
                state, pcode = state.strip().split(" ", 1)
                phone = loc[2]
                hours = (
                    loc1.lower()
                    .split("lobby hours", 1)[1]
                    .split("drive", 1)[0]
                    .replace("\n", " ")
                    .strip()
                )

                data.append(
                    [
                        "https://snbconnect.com/",
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "US",
                        "<MISSING>",
                        phone,
                        "Branch | ATM",
                        "<MISSING>",
                        "<MISSING>",
                        hours,
                    ]
                )

                p += 1
        except:
            loclist = soup.text.split("LOCATIONS AND HOURS", 1)[1]
            loclist = re.sub(pattern, "\n", loclist).strip().split("VISIT MY SITE")
            for loc in loclist:

                loc = loc.strip().splitlines()
                title = loc[0]
                address = loc[1].split(", ")
                hours = (
                    loc[2]
                    .replace("\n", " ")
                    .lower()
                    .split("lobby hours", 1)[1]
                    .split("drive", 1)[0]
                    .replace("\n", " ")
                    .strip()
                )

                state = address[-1]
                city = address[-2]
                street = " ".join(address[0 : len(address) - 2])
                state, pcode = state.split(" ", 1)
                try:
                    pcode, phone = pcode.strip().split(" ", 1)
                except:
                    phone = pcode[5:]
                    pcode = pcode[0:5]
                data.append(
                    [
                        "https://snbconnect.com/",
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "US",
                        "<MISSING>",
                        phone,
                        "Branch | ATM",
                        "<MISSING>",
                        "<MISSING>",
                        hours,
                    ]
                )

                p += 1
        if len(loclist) == 0:
            loclist = soup.text.split("Location and Hours", 1)[1]
            loc = (
                re.sub(pattern, "\n", loclist)
                .strip()
                .split("24 HOUR ATM", 1)[0]
                .splitlines()
            )
            phone = loc[0].split(" at ", 1)[1]
            hours = loc[1]
            address = loc[2].split(", ")
            state = address[-1]
            city = address[-2]
            street = " ".join(address[0 : len(address) - 2])
            state, pcode = state.lstrip().split(" ", 1)
            data.append(
                [
                    "https://snbconnect.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
                    phone.replace(".", ""),
                    "Branch | ATM",
                    "<MISSING>",
                    "<MISSING>",
                    hours,
                ]
            )

            p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
