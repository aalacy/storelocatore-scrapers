from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("sbsu_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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
    search_url = "https://sbsu.com/branch-information"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.find("table", {"class": "table"}).findAll("tr")
    locations.pop(0)
    for loc in locations:
        title = loc.find("a").text
        link = "https://sbsu.com" + loc.find("a")["href"].lstrip("..").strip()
        ptags = loc.findAll("p")
        if len(ptags) == 10:
            street = ptags[0].text
            locality = ptags[2].text
            phone = ptags[3].text
            hours = (
                ptags[4].text
                + " "
                + ptags[5].text
                + " "
                + ptags[6].text
                + " "
                + ptags[7].text
            )
        if len(ptags) == 9:
            street = ptags[0].text
            locality = ptags[1].text
            phone = ptags[2].text
            hours = (
                ptags[3].text
                + " "
                + ptags[4].text
                + " "
                + ptags[5].text
                + " "
                + ptags[6].text
            )
        if len(ptags) == 12:
            street = ptags[0].text
            locality = ptags[2].text
            phone = ptags[3].text
            hours = (
                ptags[4].text
                + " "
                + ptags[5].text
                + " "
                + ptags[6].text
                + " "
                + ptags[7].text
            )
        locality = locality.split(" ")
        if len(locality) == 3:
            city = locality[0].strip()
            state = locality[1].strip()
            pcode = locality[2].strip()
        if len(locality) == 4:
            city = locality[0].strip() + " " + locality[1].strip()
            state = locality[2].strip()
            pcode = locality[3].strip()
        hours = hours.replace("Â", "")

        hours = hours.split("Closed M-F:")[0].strip()
        hours = hours + " " + "Closed"

        hours = hours.strip()

        data.append(
            [
                "https://sbsu.com/",
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
