from sgrequests import SgRequests
from sglogging import SgLogSetup
import csv
import json
from lxml import html

logger = SgLogSetup().get_logger("carpetone_ca")
locator_domain_url = "https://www.carpetone.ca"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


headers = {
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}

session = SgRequests()


def get_data_using_skip_num_latlng():
    skip_success_list = []  # This list will be used for debugging purpose
    data_all = []
    data_list = []
    data_list_message_remvd = []
    data_list_without_duplicates = []
    skip_num_start = 0
    skip_num_end = 900  # After 800 it does not yield the data, considering future data, 900 seems to be ideal choice
    for skip_num in range(skip_num_start, skip_num_end):
        url_api = f"https://www.carpetone.ca/carpetone/api/Locations/GetClosestStores?skip={skip_num}&zipcode=M4B&latitude=56.130366&longitude=-106.346771"
        try:
            res = session.get(url_api, headers=headers)
            if res.ok:
                skip_success_list.append(skip_num)
                logger.info("Successful Skip Number: %s" % skip_num)
            data_json_raw = res.json()
            if data_json_raw:
                data_all.append(data_json_raw)
                for da in data_json_raw:
                    data_list.append(da)
                    if not "Message" in da:
                        data_list_message_remvd.append(da)
                        if da not in data_list_without_duplicates:
                            data_list_without_duplicates.append(da)
            else:
                continue

        except:
            pass
    return data_list_without_duplicates


def fetch_data():
    data_list = get_data_using_skip_num_latlng()
    items = []
    for data in data_list:
        division_code = data["DivisionCode"]
        country_code_for_canada = "C-1CAN"
        if division_code == country_code_for_canada:
            locator_domain = locator_domain_url
            page_url = data["MicroSiteURL"] or "<MISSING>"
            location_name = data["Name"] or "<MISSING>"
            sa = data["Address"]
            street_address = sa if sa else "<MISSING>"
            c = data["City"]
            city = c if c else "<MISSING>"
            state = data["State"] if data["State"] else "<MISSING>"
            country_code = "CA" or "<MISSING>"
            zip = data["Zip"] or "<MISSING>"
            store_number = (
                data["LocationNumber"] if data["LocationNumber"] else "<MISSING>"
            )
            latitude = data["Latitude"] or "<MISSING>"
            longitude = data["Longitude"] or "<MISSING>"
            r_hoo = session.get(page_url)
            data_hoo = html.fromstring(r_hoo.text, "lxml")
            data_hoo = data_hoo.xpath('//script[@type="application/ld+json"]/text()')
            data_hoo = json.loads("".join(data_hoo[0]))
            hoo = data_hoo["openingHours"]
            hours_of_operation = hoo if hoo else "<MISSING>"
            phone = data_hoo["telephone"] or "<MISSING>"
            location_type = data_hoo["@type"] or "<MISSING>"
            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            items.append(row)
        else:
            continue
    return items


def scrape():
    logger.info("Scraping Started")
    data = fetch_data()
    logger.info(f"Total Store Count: {len(data)}")
    write_output(data)


if __name__ == "__main__":
    scrape()
