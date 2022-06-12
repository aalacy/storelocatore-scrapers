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
    url = "https://gambinospizza.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select("a[href*=stores]")
    p = 0
    for div in divlist:
        stlink = div["href"]
        check = stlink.split("stores/", 1)[1].split(".", 1)[0]
        if len(check) > 2:
            continue
        else:
            pass
        stlink = "https://gambinospizza.com/" + stlink
        r = session.get(stlink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("a", {"class": "yellow"})
        for link in linklist:
            title = link.text
            link = "https://gambinospizza.com/stores/" + link["href"]
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            content1 = soup.find("div", {"class": "storeinfo"}).text.replace(
                "\xa0", " "
            )
            content1 = re.sub(pattern, "\n", content1).strip()
            content = content1.splitlines()
            m = 0
            street = content[m]
            m += 1
            try:
                city, state = content[m].split(", ", 1)
            except:
                street = street + " " + content[m]
                m += 1
                city, state = content[m].split(", ", 1)
            state, pcode = state.split(" ", 1)
            if len(state) > 2:
                street = street + " " + content[m]
                m += 1
                city, state = content[m].split(", ", 1)
                state, pcode = state.split(" ", 1)
            m += 1
            phone = content[m]

            hours = (
                content1.split("HOURS", 1)[1]
                .split("\n", 1)[1]
                .replace("\n", " ")
                .strip()
            )
            try:
                hours = hours.split("PHOT", 1)[0]
            except:
                pass
            try:
                hours = hours.split("Large", 1)[0]
            except:
                pass
            try:
                hours = hours.split("CATER", 1)[0]
            except:
                pass
            try:
                hours = hours.split("Monday-Friday PARTY ROOM", 1)[0]
            except:
                pass
            try:
                hours = hours.split("DAIL", 1)[0]
            except:
                pass
            try:
                hours = hours.split("Inside", 1)[0]
            except:
                pass
            try:
                hours = hours.split("Closed for: Easter", 1)[0]
            except:
                pass
            if phone.replace("-", "").replace("(", "").replace(")", "").isdigit():
                pass
            else:
                phone = "<MISSING>"
            try:
                longt, lat = (
                    soup.find("iframe")["src"]
                    .split("!2d", 1)[1]
                    .split("!3m", 1)[0]
                    .split("!3d", 1)
                )
            except:
                longt = lat = "<MISSING>"
            try:
                lat = lat.split("!2m", 1)[0]
            except:
                pass
            data.append(
                [
                    "https://gambinospizza.com/",
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
                    hours.replace("•", " ").strip(),
                ]
            )

            p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
