from bs4 import BeautifulSoup
import csv
import re

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
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
    streetlist = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.howardbank.com/branch-locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"id": "block-menu-menu-branch-location"}).findAll("a")

    p = 0
    for div in divlist:

        title = div.text
        link = div["href"]

        if link.replace("locations/", "locations") == "/branch-locations":
            continue
        if "https" in link:
            pass
        else:
            link = "https://www.howardbank.com" + link
        if link in streetlist:
            continue
        streetlist.append(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        if "commerical-loan-office" in link:
            hours = "<MISSING>"
            ltype = "Branch"
            ctlist = soup.find("section", {"class": "post-content"}).findAll("p")
            for ct in ctlist:
                ct = ct.text.splitlines()
                title = ct[0]
                street = ct[1]
                city, state = ct[2].split(", ", 1)
                state, pcode = state.lstrip().split(" ", 1)
                try:
                    phone = ct[3]
                except:
                    phone = "<MISSING>"
        else:
            ltype = "Branch | ATM"
            content1 = soup.find("div", {"class": "row branch-info"})
            content1 = re.sub(cleanr, "\n", str(content1))
            content1 = re.sub(pattern, "\n", content1).strip()
            content = content1.splitlines()
            street = content[1]
            city, state = content[2].split(" ", 1)
            city = city.replace(",", "")
            state, pcode = state.lstrip().split(" ", 1)
            phone = content[3]
            hours = (
                content1.split("Branch Hours:", 1)[1]
                .split("Services:", 1)[0]
                .replace("\n", " ")
                .strip()
            )
        if len(state.strip()) > 3:
            city = city + " " + state
            city = city.replace(",", "").strip()
            state, pcode = pcode.split(" ", 1)
        if "TEMPORARY CLOSURE" in soup.text:
            title = title + "- " + "TEMPORARY CLOSED "
        data.append(
            [
                "https://www.howardbank.com",
                link,
                title.replace("\xa0", "").strip(),
                street.replace("\xa0", ""),
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone.replace("\xa0", ""),
                ltype,
                "<MISSING>",
                "<MISSING>",
                hours.replace("\u200b", ""),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
