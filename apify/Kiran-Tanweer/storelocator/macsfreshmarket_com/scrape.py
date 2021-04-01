from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser


logger = SgLogSetup().get_logger("macsfreshmarket_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    search_url = "https://macsfreshmarket.com/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.find("ul", {"class": "sub-menu"}).findAll("a")
    for loc in locations:
        title = loc.text
        link = loc["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        divs = soup.findAll(
            "div",
            {
                "class": "mp-row-fluid motopress-row mpce-dsbl-margin-left mpce-dsbl-margin-right"
            },
        )
        div = divs[3].find("h3")
        if div is None:
            info = divs[2]
        else:
            info = divs[3]
        address = info.find("h3").text
        address = address.replace("\n", "")
        phone = info.find("a").text
        hours = info.findAll(["h3", "h4"])
        if len(hours) == 3:
            hoo = hours[1].text
        if len(hours) == 4:
            hoo = hours[2].text
        hoo = hoo.replace("\n", " ")
        hoo = hoo.replace("Open 7 Days A Week!", "").strip()
        hoo = hoo.rstrip("• 7 Days A Week!").strip()
        hoo = hoo.lstrip("Hours:").strip()
        if hoo.find("Mon") == -1:
            hoo = "Mon-Sun: " + hoo
        parsed = parser.parse_address_intl(address)
        country = parsed.country if parsed.country else "<MISSING>"
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"

        if state == "Louisiana":
            state = "LA"
        if state == "Arkansas":
            state = "AR"
        data.append(
            [
                "https://macsfreshmarket.com/",
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
                hoo,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
