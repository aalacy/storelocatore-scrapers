import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
import lxml.html
import json

logger = SgLogSetup().get_logger("vim_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }

    base_url = "https://www.vim.com"
    r = session.get("https://www.vim.com/apps/store-locator", headers=headers)
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "vim"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "https://www.vim.com/apps/store-locator"
    list_locations = r.text.split("markersCoords.push({")
    for script in list_locations[1:-2]:
        soup_location = script.split("});")[0]

        list_location = soup_location.split(",")
        latitude = list_location[0].replace("lat:", "").strip()
        longitude = list_location[1].replace("lng:", "").strip()
        store_number = list_location[2].replace("id:", "").strip()

        address_str = (
            list_location[5]
            .replace("address:'", "")
            .strip()
            .replace("&#039;", '"')
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )
        address_soup = BeautifulSoup(address_str, "lxml")
        address_list = list(address_soup.stripped_strings)
        location_name = address_list[0]
        street_address = address_list[1]
        city = address_list[2]

        sz_str = (
            list_location[6]
            .replace("address:'", "")
            .strip()
            .replace("&#039;", '"')
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )
        sz_str_soup = BeautifulSoup(sz_str, "lxml")
        sz_str_list = list(sz_str_soup.stripped_strings)
        if len(sz_str_list) > 1:
            state = sz_str_list[0]
            zipp = sz_str_list[1]
        else:
            zipp = sz_str_list[0]
            state = "<MISSING>"

        country_code = "US"

        logger.info(f"pulling info for store ID: {store_number}")
        r_phone_hour = session.get(
            "https://stores.boldapps.net/front-end/get_store_info.php?shop=vimstores.myshopify.com&data=detailed&store_id="
            + store_number,
            headers=headers,
        )
        store_sel = lxml.html.fromstring(json.loads(r_phone_hour.text)["data"])

        phone = "".join(store_sel.xpath('//span[@class="phone"]/text()')).strip()
        hours_of_operation = ""
        hours = store_sel.xpath('//span[@class="hours"]/text()')
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                day = "".join(hour).strip().split(" ", 1)[0].strip()
                time = "".join(hour).strip().split(" ", 1)[1].strip()
                hours_list.append(day + ":" + time)

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        store = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            page_url,
        ]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
