from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("burton_com")

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
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


locations = [
    "https://www.shopbedmart.com/hi/locations/",
    "https://www.shopbedmart.com/nw/locations/",
]


def fetch_data():
    data = []
    url = "https://www.burton.com/ca/en/stores"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    locations = soup.findAll("figure", {"class": "store-wrap north-america"})
    for loc in locations:
        title = loc.find("h3", {"class": "text-h3-display"}).text.strip()
        street = loc.find("span", {"itemprop": "streetAddress"}).text.strip()
        city = loc.find("span", {"itemprop": "addressLocality"}).text.strip()
        state = loc.find("span", {"itemprop": "addressRegion"}).text.strip()
        pcode = loc.find("span", {"itemprop": "postalCode"}).text.strip()

        if (
            state == "VT"
            or state == "CO"
            or state == "NY"
            or state == "CA"
            or state == "MA"
            or state == "UT"
            or state == "PA"
            or state == "IL"
            or state == "ME"
            or state == "MT"
        ):
            country = "US"
        else:
            country = "CAN"
        phone = loc.find("span", {"itemprop": "telephone"}).text.strip()
        link = loc.find("span", {"class": "view-details"}).find("a")["href"].strip()
        link = "https://www.burton.com/" + link
        hours = loc.find("meta", {"itemprop": "openingHours"})
        if hours is None:
            hours = "<MISSING>"
        else:
            hours = hours["content"]
        hours = hours.replace("Mo-Sa", "Mon-Sat")
        hours = hours.replace("Mo-Su", "Mon-Sun")
        hours = hours.replace("Mo-Th", "Mon-Thurs")
        if street == "675 Lionshead Place":
            addr = loc.find("p", {"class": "address"}).text
            addr = addr.split("\n")
            street = addr[0] + " " + addr[1]
            street = street.strip()
        data.append(
            [
                "https://www.burton.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                country,
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
