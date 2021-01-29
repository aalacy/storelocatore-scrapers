from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("1000degreespizza_com")

session = SgRequests()

headers = {
    "authority": "www.1000degreespizza.com",
    "method": "GET",
    "path": "/pizza-place-near-me-locations/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "_ga=GA1.2.151889300.1611623194; _gid=GA1.2.2137413542.1611623194; _gat=1",
    "referer": "https://www.1000degreespizza.com/pizza-place-near-me-locations/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
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
    url = "https://www.1000degreespizza.com/pizza-place-near-me-locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    locations = soup.findAll("section", {"class": "av_toggle_section"})
    for loc in locations:
        info = loc.findAll("div", {"class": "location-1000d"})
        for store in info:
            atgs = store.findAll("a")
            if len(atgs) > 0:
                link = atgs[-1]["href"]
                if link == "../best-pizza-place-coral-woodmore-maryland/":
                    link = "https://www.1000degreespizza.com/best-pizza-place-coral-woodmore-maryland/"
            if len(atgs) == 0:
                link = "https://www.1000degreespizza.com/pizza-place-near-me-locations/#toggle-id-11"
            title = store.find("h3").text
            addr = store.find("p")
            addr = str(addr)
            addr = addr.lstrip("<p>")
            addr = addr.rstrip("</p>")
            addr = addr.split("<br/>")
            if len(addr) == 3:
                street = addr[0].strip()
                locality = addr[1].strip()
                locality = locality.split(",")
                city = locality[0]
                state = locality[1]
                pcode = "<MISSING>"
                phone = addr[2].strip()
                hours = "<MISSING>"
            if len(addr) == 2:
                street = addr[0].strip()
                locality = addr[1].strip()
                locality = locality.split(",")
                city = locality[0]
                state = locality[1]
                pcode = "<MISSING>"
                phone = "<MISSING>"
                hours = "Coming Soon"
            if len(addr) == 4:
                street = addr[0].strip()
                locality = addr[1].strip()
                locality = locality.split(",")
                city = locality[0]
                state = locality[1]
                pcode = "<MISSING>"
                phone = addr[2].strip()
                phone = phone.split('"d3ph">')[1].split("</span>")[0].strip()
                hours = "<MISSING>"
            if len(addr) == 7:
                street = addr[0].strip()
                locality = addr[1].strip()
                locality = locality.split(",")
                city = locality[0]
                state = locality[1]
                pcode = "<MISSING>"
                hours = "<MISSING>"
                phone = addr[2].strip()
                phone = phone.split('"d3ph">')[1].split("</span>")[0].strip()
            state = state.strip()

            if state == "Delaware":
                state = "DE"
            if state == "Florida":
                state = "FL"
            if state == "Georgia":
                state = "GA"
            if state == "Iowa":
                state = "IA"
            if state == "Michigan":
                state = "MI"
            if state == "Minnesota":
                state = "MN"
            if state == "New Jersey":
                state = "NJ"
            if state == "South Dakota":
                state = "SD"
            if state == "Tennessee":
                state = "TN"
            if state == "Texas":
                state = "TX"
            if state == "Utah":
                state = "UT"
            data.append(
                [
                    "www.1000degreespizza.com/",
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
