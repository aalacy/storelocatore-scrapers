from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("gardenfreshmarket_com")

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
    url = "https://www.gardenfreshmarket.com/store-locator"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    blocks = soup.findAll("div", {"class": "col sqs-col-4 span-4"})
    for block in blocks:
        info = block.find("div", {"class": "sqs-block-content"}).findAll("p")
        title = info[0].text
        address = str(info[1])
        address = address.split('pre-wrap;">')[1]
        address = address.rstrip("</p>")
        address = address.replace(",", "<br/>")
        address = address.split("<br/>")
        street = address[0].strip()
        city = address[1].strip()
        state = address[2].strip()
        phone = address[3].strip()
        info2 = block.find("div", {"class": "sqs-block map-block sqs-block-map"})[
            "data-block-json"
        ]
        info2 = str(info2)
        lat = info2.split('"mapLat":')[1].split(",")[0]
        lng = info2.split('"mapLng":')[1].split(",")[0]
        pcode = (
            info2.split('"addressLine2":"')[1].split('","')[0].split(",")[-1].strip()
        )

        data.append(
            [
                "https://www.gardenfreshmarket.com/",
                "https://www.gardenfreshmarket.com/store-locator",
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
                lng,
                "<MISSING>",
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
