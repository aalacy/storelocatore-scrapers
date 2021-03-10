from bs4 import BeautifulSoup
import csv
import time
import re
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mgmwineandspirits_com")

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://mgmwineandspirits.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    locations = soup.findAll("a", {"class": "btn locations"})
    for loc in locations:
        link = "https://mgmwineandspirits.com" + loc["href"]
        p = session.get(link, headers=headers, verify=False)
        bs = BeautifulSoup(p.text, "html.parser")
        title = bs.find(
            "div", {"class": "page-header visible-lg visible-md"}
        ).text.strip()
        hours = bs.find("section", {"id": "store-hours"}).text
        hours = re.sub(pattern, "\n", hours)
        hours = re.sub(cleanr, " ", hours)
        hours = hours.replace("\n", " ")
        hours = hours.strip()
        hours = hours.lstrip("Store Hours")
        hours = hours.rstrip(
            " Walk in or Call us! Both in store and curbside services available. Curbside Service Call 507-366-6460 with your order. Thank you and stay safe!"
        )
        phone = bs.find("span", {"class": "btn phone-number"}).text
        address = bs.find("a", {"class": "btn address"})
        address = str(address)
        address = address.split("<span>")[1].split("</span>")[0]
        address = address.replace("<br/>", ",")
        address = address.split(",")
        street = address[0].strip()
        city = address[1].strip()
        locality = address[2].strip()
        locality = locality.split(" ")
        state = locality[0]
        pcode = locality[1]

        data.append(
            [
                "https://mgmwineandspirits.com/",
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
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
                hours,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
