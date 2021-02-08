import csv
from sgrequests import SgRequests
from sglogging import sglog

website = "gigiscupcakesusa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        temp_list = []  # ignoring duplicates
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
        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    final_data = []
    if True:
        url = "https://easylocator.net/ajax/search_by_lat_lon_geojson/gigiscupcakesusa/24.9056/67.0822/0/50"
        loclist = session.get(url, headers=headers, verify=False).json()["physical"]
        for loc in loclist:
            store = loc["properties"]["location_number"]
            title = loc["properties"]["name"]
            street = loc["properties"]["street_address"]
            city = loc["properties"]["city"]
            state = loc["properties"]["state_province"]
            pcode = loc["properties"]["zip_postal_code"]
            phone = loc["properties"]["phone"]
            if not phone:
                phone = "<MISSING>"
            link = loc["properties"]["website_url"]
            if not link:
                link = "<MISSING>"
            hours = loc["properties"]["additional_info"]
            hours = hours.split('<div style="margin-bottom: 0.6em;">', 1)[1].split(
                '<div style="margin-bottom: 0.6em;">', 1
            )[0]
            hours = (
                hours.replace("<br/>", "")
                .replace("</div>", "")
                .replace("\n", " ")
                .replace("<br>", "")
                .strip()
            )
            hours = hours.split("<a", 1)[0]
            if not hours:
                hours = "<MISSING>"
            lat = loc["properties"]["lat"]
            longt = loc["properties"]["lon"]
            final_data.append(
                [
                    "https://gigiscupcakesusa.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )
    return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
