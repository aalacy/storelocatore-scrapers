from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("yvesdelormeoutlet_com")

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
    search_url = "https://usa.yvesdelormeoutlet.com//plugincompany_storelocator/storelocation/storesjson/?"
    stores_req = session.get(search_url, headers=headers).json()
    for loc in stores_req:
        title = loc["locname"]
        storeid = loc["entity_id"]
        lat = loc["lat"]
        lng = loc["lng"]
        street1 = loc["address"]
        street2 = loc["address2"]
        city = loc["city"]
        state = loc["state"]
        country = loc["country"]
        pcode = loc["postal"]
        phone = loc["phone"]
        hours = loc["schedule"]
        link = loc["pageurl"]
        hours = BeautifulSoup(hours, "html.parser")
        hours = hours.text
        hours = hours.replace("day", "day ")
        hours = hours.replace("am", "am ")
        hours = hours.replace("pm", "pm ")
        hours = hours.replace("ClosedClosed", "Closed").strip()
        street = street1 + " " + street2
        street = street.strip()
        if state == "":
            state = "<MISSING>"
        data.append(
            [
                "https://usa.yvesdelormeoutlet.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                country,
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
