from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("sitnsleep_com")

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
    url = "https://www.sitnsleep.com/js/app.851c759c.js"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    bs = str(soup)
    bs = bs.split("stores:")[1].split('}}};t["a"]=s},')[0]
    locs = bs.split("{about:")
    for loc in locs:
        if loc != "[":
            title = loc.split(',name:"')[1].split('",')[0]
            street = loc.split(',street:"')[1].split('",')[0]
            street = street.replace("<br/>", " ")
            city = loc.split('{city:"')[1].split('",')[0]
            state = loc.split(',state:"')[1].split('",')[0]
            pcode = loc.split(',zip:"')[1].split('"}')[0]
            country = loc.split(',country:"')[1].split('",')[0]
            hours = loc.split(",hours:'")[1].split("',l")[0]
            week = hours.split("<p><strong>")[1].split("</p>")[0]
            week = week.replace("</strong>", "")
            sat = hours.split('hours-saturday">')[1].split("</p>")[0]
            sat = sat.replace("</strong>", "")
            sun = hours.split('hours-sunday">')[1].split("</p>")[0]
            sun = sun.replace("</strong>", "")
            hoo = week + ", " + sat + ", " + sun
            lat = loc.split('latitude:"')[1].split('",')[0]
            lng = loc.split('longitude:"')[1].split('",')[0]
            phone = loc.split(',phone:"')[1].split('",')[0]
            link = loc.split('route:"')[1].split('",')[0]
            link = link.rstrip('"},')
            page = "https://www.sitnsleep.com/store/" + link

            data.append(
                [
                    "www.sitnsleep.com",
                    page,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    country,
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    lng,
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
