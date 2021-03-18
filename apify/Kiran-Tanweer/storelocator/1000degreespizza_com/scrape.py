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
    locations = soup.findAll("div", {"class": "location-1000d"})
    for info in locations:
        atgs = info.findAll("a")

        details = info.text.strip()
        details = details.split("\n")
        if len(details) == 4:
            title = details[0].strip()
            street = details[1].strip()
            locality = details[2].strip()
            phone = details[3].strip()
        if len(details) == 5:
            if details[-1].find("CLOSED TEMPORARILY") != -1:
                title = details[0].strip()
                street = details[1].strip()
                locality = details[2].strip()
                phone = details[3].strip()
            else:
                title = details[0].strip()
                street = details[-3].strip()
                locality = details[-2].strip()
                phone = details[-1].strip()
        if phone == "OPENING SOON!":
            phone = "<MISSING>"
            hours = "OPENING SOON!"
        else:
            hours = "<MISSING>"
        try:
            link = atgs[-1]
            link = str(link)
            link = link.split("<picture>")[0]
            link = link.replace('<a href="', "")
            link = link.replace('" style="margin-top: 20px;">', "")
            link = link.replace("</a>", "")
            link = link.replace(
                '<img alt="" src="../wp-content/uploads/2020/01/view-store-btn.jpg"/>',
                "",
            )
            if link.find("..") != -1:
                link = link.replace("..", "https://www.1000degreespizza.com")
        except IndexError:
            link = "<MISSING>"
        locality = locality.split(",")
        city = locality[0].strip()
        state = locality[1].strip()

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
                "<MISSING>",
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
