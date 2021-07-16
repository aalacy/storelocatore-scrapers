from bs4 import BeautifulSoup
import csv
import time
from sgscrape import sgpostal as parser
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bedzzzexpress_com")

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
    url = "https://bedzzzexpress.com/stores/"
    r = session.get(url, headers=headers, verify=False)
    soups = BeautifulSoup(r.text, "html.parser")
    scripts = soups.findAll("script")[15]
    scripts = str(scripts)
    scripts = scripts.lstrip(
        '<script type="text/javascript">\n  // <![CDATA[\n jQuery(document).ready(\n   function()\n     {\n       jQuery("#map1").dmxGoogleMaps(\n         {"dataSource": "", "dataSourceType": "dynamic", "zoom": 6, "markers": [ {'
    )
    coords = scripts.split('"latitude": ')
    linklist = soups.find("div", {"id": "StoreList"})
    sections = linklist.findAll("div", {"class": "fgm-section"})
    for sec in sections:
        info = sec.find("a", {"class": "sot_store_header_link"})
        link = "https://bedzzzexpress.com" + info["href"]
        title = info.text
        allinfo = sec.findAll("p")
        storeid = allinfo[0].find("input")["value"]
        address = str(allinfo[1])
        address = address.lstrip("<p>")
        address = address.rstrip("</p>")
        address = address.strip()
        address = address.replace("<br/>", " ")
        address = address.replace(",", "")
        phone = allinfo[2].find("a").text
        hours = allinfo[5].text.strip()
        hours = hours.replace("pmS", "pm S")
        if (
            hours
            == "This is a Bedzzz Central Warehouse and Corporate Offices  Customer Pick Up Only"
        ):
            hours = "<MISSING>"
        parsed = parser.parse_address_usa(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"
        search = '"' + storeid + '"'
        for c in coords:
            if c.find(search) != -1:
                lat = c.split(",")[0]
                lng = c.split('"longitude":')[1].split(",")[0]

        data.append(
            [
                "https://bedzzzexpress.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                storeid,
                phone,
                "<MISSING>",
                lat,
                lng,
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
