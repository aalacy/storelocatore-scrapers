import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser

logger = SgLogSetup().get_logger("ontheborder_com")

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
                row[8],
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    search_url = "https://www.ontheborder.com/wp-admin/admin-ajax.php?searchFallback=false&page=1&sort%5B0%5D%5Bfield%5D=name&sort%5B0%5D%5Border%5D=asc&perpage=0&action=mapsvg_data_get_all&map_id=405&table=database"
    stores_req = session.get(search_url, headers=headers).json()
    for loc in stores_req["objects"]:
        address = loc["location"]["address"]["formatted"]
        lat = loc["location"]["lat"]
        lng = loc["location"]["lng"]
        title = loc["name"]
        isloc = loc["post"]
        if isloc is not None:
            link = loc["post"]["guid"]
            hours = loc["post"]["acf"]["hours"]
            hoo = ""
            for hr in hours:
                day = hr["day_or_day_range"]
                time = hr["hour_range"]
                hoo = hoo + " " + day + " " + time
            phone = loc["post"]["acf"]["phone_number"]
            storeid = loc["post"]["ID"]
        else:
            link = "<MISSING>"
            hours = "<MISSING>"
            phone = "<MISSING>"
            storeid = "540"
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
        hours = str(hours)
        hours = hours.replace("'", "")
        hours = hours.replace(",", "")
        hours = hours.replace("[", "")
        hours = hours.replace("]", "")
        hours = hours.replace("{", "")
        hours = hours.replace("}", "")
        hours = hours.replace(":", "")
        hours = hours.replace("day_or_day_range", "")
        hours = hours.replace("hour_range", "")
        hours = hours.replace("  ", " ").strip()

        data.append(
            [
                "https://www.ontheborder.com/",
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
