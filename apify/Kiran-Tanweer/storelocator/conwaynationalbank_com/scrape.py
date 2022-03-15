from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("conwaynationalbank_com")

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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    search_url = "http://conwaynationalbank.com/locations_hours_h.cfm"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    division = soup.find("div", {"class": "content_home"})
    hours = division.findAll("p")[1].text.strip()
    hours = hours.replace("Drive-up windows open at 8:30 a.m.", "")
    hours = hours.replace("    ", " ")
    hours = hours.strip()
    locs = soup.find("table").findAll("td")
    count = 1
    for info in locs:
        loc = info.text.strip()
        loc = loc.replace("			       ", ", ")
        loc = re.sub(pattern, ", ", loc)
        loc = re.sub(cleanr, ", ", loc)
        loc = loc.split(",")
        if len(loc) == 6:
            title = loc[0].strip()
            street = loc[1].strip()
            city = loc[3].strip()
            locality = loc[4].strip()
            phone = loc[-1].strip()
        if len(loc) == 5:
            title = loc[0].strip()
            street = loc[1].strip()
            city = loc[2].strip()
            locality = loc[3].strip()
            phone = loc[-1].strip()
        if len(loc) == 7:
            title = loc[0].strip()
            street = loc[1].strip()
            city = loc[4].strip()
            locality = loc[5].strip()
            phone = loc[-1].strip()
        num = str(count) + ")"

        title = title.replace(num, "").strip()
        count = count + 1
        locality = locality.replace("\xa0", " ")

        locality = locality.split(" ")
        state = locality[0].strip()
        pcode = locality[1].strip()

        data.append(
            [
                "http://conwaynationalbank.com/",
                search_url,
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
