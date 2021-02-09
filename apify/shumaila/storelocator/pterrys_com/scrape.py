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
    titlelist = []
    data = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://pterrys.com/locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("div", {"class": "itemsCollectionContainer"}).select(
        "a[href*=locations]"
    )
    p = 0
    for link in linklist:
        link = "https://pterrys.com" + link["href"]
        if link in titlelist:
            continue
        titlelist.append(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title").text.split("-")[0]
        divlist = soup.findAll("div", {"class": "itemContent"})
        address = re.sub(cleanr, "\n", str(divlist[0])).strip()
        address = re.sub(pattern, "\n", str(address)).strip().splitlines()
        street = address[1]
        city, state = address[2].replace(",", "").split(" ", 1)
        try:
            state, pcode = state.strip().split(" ", 1)
        except:
            pcode = address[3]
        hours = re.sub(cleanr, "\n", str(divlist[1])).strip()
        hours = (
            re.sub(pattern, "\n", str(hours))
            .replace("\n", " ")
            .strip()
            .replace("Hours ", "")
        )
        phone = re.sub(cleanr, "\n", str(divlist[2])).strip()
        phone = re.sub(pattern, "\n", str(phone)).strip().split("\n")[1]

        try:
            temp, pcode = pcode.strip().split(" ", 1)
            city = city + " " + state
            state = temp
        except:
            pass
        try:
            hours = hours.split("hours:", 1)[1].strip()
        except:
            pass
        try:
            hours = hours.split("Hours:", 1)[1].strip()
        except:
            pass
        try:
            hours = hours.split("HOURS ", 1)[1].strip()
        except:
            pass
        data.append(
            [
                "https://pterrys.com/",
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
                "<MISSING>",
                "<MISSING>",
                hours.replace("&amp;", "&"),
            ]
        )
        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
