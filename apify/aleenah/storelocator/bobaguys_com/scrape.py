from bs4 import BeautifulSoup
import csv
import re
import time
import usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bobaguys_com")

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
    # Your scraper here
    p = 0
    all = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.bobaguys.com/"
    r = session.get(url, headers=headers, verify=False)

    soup = BeautifulSoup(r.text, "html.parser")
    urls = soup.find("li", {"class": "folder"}).find_all("a")

    del urls[0]

    for url in urls:
        url = "https://www.bobaguys.com" + url["href"]

        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        divs = soup.find_all("div", {"class": "col sqs-col-4 span-4"})
        if len(divs) == 0:
            divs = soup.find_all("div", {"class": "col sqs-col-6 span-6"})

        for div in divs:
            try:
                div.find(
                    "div", {"class": "sqs-block html-block sqs-block-html"}
                ).find_all("p")
            except:
                continue
            content = re.sub(
                cleanr,
                "\n",
                str(div).replace("San Francisco Mission location", "").strip(),
            )
            content = re.sub(pattern, "\n", content).lstrip()
            title = content.split("\n", 1)[0]

            try:
                address = content.split("\n", 1)[1].split("Mon")[0]
                hours = "Mon" + content.split("Mon")[1]
            except:
                try:
                    address = content.split("\n", 1)[1].split("Wed")[0]
                    hours = "Wed" + content.split("Wed")[1]
                except:
                    try:
                        address = content.split("\n", 1)[1].split("Temp")[0]
                        hours = "Temp" + content.split("Temp")[1]
                    except:
                        continue  # closed

            address = address.replace("\n", " ")

            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1

            street = street.lstrip().replace(",", "")
            city = city.lstrip().replace(",", "")
            state = state.lstrip().replace(",", "")
            pcode = pcode.lstrip().replace(",", "")
            hours = hours.replace("\n", " ")
            if len(state) < 2:
                state = "CA"
            try:
                hours = hours.split("Dir")[0]
            except:
                pass
            all.append(
                [
                    "https://www.bobaguys.com",
                    url,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",  # store #
                    "<MISSING>",  # phone
                    "<MISSING>",  # type
                    "<MISSING>",  # lat
                    "<MISSING>",  # long
                    hours,  # timing
                ]
            )

            p += 1

    return all


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
