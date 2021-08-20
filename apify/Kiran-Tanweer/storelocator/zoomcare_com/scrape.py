import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("zoomcare_com")

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
                row[4],
                row[5].strip(),
                row[6],
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    url = "https://api-prod.zoomcare.com/v1/schedule/clinics"
    stores_req = session.get(url, headers=headers).json()
    for loc in stores_req:
        street = loc["address"]["line1"]
        street2 = loc["address"]["line2"]
        if street2 is not None:
            street = street + " " + street2
        else:
            street = street.strip()
        city = loc["address"]["city"]
        state = loc["address"]["state"]
        pcode = loc["address"]["postalCode"]
        storeid = loc["clinicId"]
        title = loc["name"]
        lat = loc["address"]["latitude"]
        lng = loc["address"]["longitude"]
        hours = loc["clinicHoursText"]
        hours = hours.replace("| ", ",")

        data.append(
            [
                "https://www.zoomcare.com/",
                "https://www.zoomcare.com/locations",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                storeid,
                "<MISSING>",
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
