import csv
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("mackenzieriverpizza.com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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


def fetch_data():

    base_link = "https://www.mackenzieriverpizza.com/locations/"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "apbct_site_landing_ts=1623281233; apbct_site_referer=UNKNOWN; ct_timezone=-4; wordpress_apbct_antibot=d4e62ddad8ed65fedbfcd931b3777f82e227f8eafa79d0a2b196edb104d4ea36; ct_checkjs=708047937; _ga=GA1.2.938144467.1623281238; _gid=GA1.2.1313817051.1623281238; apbct_prev_referer=https%3A%2F%2Fwww.mackenzieriverpizza.com%2F; ct_fkp_timestamp=0; ct_ps_timestamp=1623307848; apbct_visible_fields=%7B%220%22%3A%7B%22visible_fields%22%3A%22s%22%2C%22visible_fields_count%22%3A1%2C%22invisible_fields%22%3A%22%22%2C%22invisible_fields_count%22%3A0%7D%2C%221%22%3A%7B%22visible_fields%22%3A%22mpfy_search_query%22%2C%22visible_fields_count%22%3A1%2C%22invisible_fields%22%3A%22%22%2C%22invisible_fields_count%22%3A0%7D%7D; apbct_timestamp=1623308216; apbct_page_hits=39; apbct_cookies_test=%257B%2522cookies_names%2522%253A%255B%2522apbct_timestamp%2522%252C%2522apbct_site_landing_ts%2522%252C%2522apbct_page_hits%2522%255D%252C%2522check_value%2522%253A%2522e56dd8cfb38344738e7fa2edda0f7776%2522%257D; apbct_urls=%7B%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fbeavercreek%5C%2F%3Fmpfy_map%3D752%26mpfy-pin%3D780%22%3A%5B1623306184%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fbillings-west%5C%2F%3Fmpfy_map%3D752%22%3A%5B1623307320%2C1623307552%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fbillings-west%5C%2F%3Fmpfy_map%3D752%26mpfy-pin%3D777%22%3A%5B1623307321%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fbillings-west%5C%2F%22%3A%5B1623307555%2C1623307567%2C1623307818%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fbillings-west%5C%2F%3Fmpfy-pin%3D777%22%3A%5B1623307557%2C1623307568%2C1623307818%2C1623307842%5D%2C%22www.mackenzieriverpizza.com%5C%2Fwp-content%5C%2Fthemes%5C%2FDivi%5C%2Fincludes%5C%2Fbuilder%5C%2Ffrontend-builder%5C%2Fbuild%5C%2Ffrontend-builder-scripts.js.map%22%3A%5B1623307805%2C1623307825%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fkalispell-south%5C%2F%3Fmpfy_map%3D752%22%3A%5B1623307847%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fkalispell-south%5C%2F%3Fmpfy_map%3D752%26mpfy-pin%3D763%22%3A%5B1623307848%5D%2C%22www.mackenzieriverpizza.com%5C%2Fwp-content%5C%2Fthemes%5C%2FDivi%5C%2Fincludes%5C%2Fbuilder%5C%2Ffrontend-builder%5C%2Fbuild%5C%2Ffrontend-builder-global-functions.js.map%22%3A%5B1623307849%5D%2C%22www.mackenzieriverpizza.com%5C%2Fwp-content%5C%2Fthemes%5C%2FDivi%5C%2Fjs%5C%2Fcustom.js.map%22%3A%5B1623308216%5D%7D; ct_pointer_data=%5B%5B358%2C11%2C123204%5D%2C%5B56%2C436%2C123306%5D%5D",
        "Host": "www.mackenzieriverpizza.com",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "mackenzieriverpizza.com"

    links = base.find(class_="mpfy-map-canvas-shell-outer").div.find_all("a")
    items = base.find_all(class_="mpfy-mll-location")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "pins: [{" in str(script):
            script = str(script)
            break
    js = "[" + script.split("pins: [")[1].split("}],")[0] + "}]"
    stores = json.loads(js)

    headers2 = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "apbct_site_landing_ts=1623281233; apbct_site_referer=UNKNOWN; ct_timezone=-4; wordpress_apbct_antibot=d4e62ddad8ed65fedbfcd931b3777f82e227f8eafa79d0a2b196edb104d4ea36; ct_checkjs=708047937; _ga=GA1.2.938144467.1623281238; _gid=GA1.2.1313817051.1623281238; apbct_prev_referer=https%3A%2F%2Fwww.mackenzieriverpizza.com%2F; ct_fkp_timestamp=0; ct_ps_timestamp=1623308222; apbct_visible_fields=%7B%220%22%3A%7B%22visible_fields%22%3A%22s%22%2C%22visible_fields_count%22%3A1%2C%22invisible_fields%22%3A%22%22%2C%22invisible_fields_count%22%3A0%7D%2C%221%22%3A%7B%22visible_fields%22%3A%22mpfy_search_query%22%2C%22visible_fields_count%22%3A1%2C%22invisible_fields%22%3A%22%22%2C%22invisible_fields_count%22%3A0%7D%7D; ct_pointer_data=%5B%5B358%2C11%2C123204%5D%2C%5B56%2C436%2C123306%5D%5D; apbct_timestamp=1623308442; apbct_page_hits=42; apbct_cookies_test=%257B%2522cookies_names%2522%253A%255B%2522apbct_timestamp%2522%252C%2522apbct_site_landing_ts%2522%252C%2522apbct_page_hits%2522%255D%252C%2522check_value%2522%253A%2522f99e4d0e6ba80a0b11b32f97c0592d08%2522%257D; apbct_urls=%7B%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fbillings-west%5C%2F%3Fmpfy_map%3D752%22%3A%5B1623307320%2C1623307552%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fbillings-west%5C%2F%3Fmpfy_map%3D752%26mpfy-pin%3D777%22%3A%5B1623307321%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fbillings-west%5C%2F%22%3A%5B1623307555%2C1623307567%2C1623307818%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fbillings-west%5C%2F%3Fmpfy-pin%3D777%22%3A%5B1623307557%2C1623307568%2C1623307818%2C1623307842%5D%2C%22www.mackenzieriverpizza.com%5C%2Fwp-content%5C%2Fthemes%5C%2FDivi%5C%2Fincludes%5C%2Fbuilder%5C%2Ffrontend-builder%5C%2Fbuild%5C%2Ffrontend-builder-scripts.js.map%22%3A%5B1623307805%2C1623307825%2C1623308225%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fkalispell-south%5C%2F%3Fmpfy_map%3D752%22%3A%5B1623307847%2C1623308442%5D%2C%22www.mackenzieriverpizza.com%5C%2Fmap-location%5C%2Fkalispell-south%5C%2F%3Fmpfy_map%3D752%26mpfy-pin%3D763%22%3A%5B1623307848%5D%2C%22www.mackenzieriverpizza.com%5C%2Fwp-content%5C%2Fthemes%5C%2FDivi%5C%2Fincludes%5C%2Fbuilder%5C%2Ffrontend-builder%5C%2Fbuild%5C%2Ffrontend-builder-global-functions.js.map%22%3A%5B1623307849%5D%2C%22www.mackenzieriverpizza.com%5C%2Fwp-content%5C%2Fthemes%5C%2FDivi%5C%2Fjs%5C%2Fcustom.js.map%22%3A%5B1623308216%5D%2C%22www.mackenzieriverpizza.com%5C%2Flocations%5C%2F%22%3A%5B1623308219%5D%7D",
        "Host": "www.mackenzieriverpizza.com",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    session = SgRequests()

    for i, item in enumerate(items):

        location_name = (
            item.find(class_="mpfy-mll-l-title").text.strip().split("\t")[0].strip()
        )
        raw_address = item.p.text.split("|")
        street_address = raw_address[0].strip()
        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[1].strip().replace("Washington", "WA")
        zip_code = city_line[2].strip()
        country_code = "US"
        store_number = item["data-id"]

        # Get hours from page
        link = links[i]["href"] + "&mpfy-pin=" + links[i]["data-id"]
        log.info(link)
        req = session.get(link, headers=headers2)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = (
            base.find_all("meta")[3]["content"]
            .split("HOURS")[1]
            .split("HAPP")[0]
            .split("DAILY SPEC")[0]
            .replace("\r\n", " ")
            .strip()
        )

        # Get lat/lng from json
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        for store in stores:
            if store_number == str(store["id"]):
                latitude = store["latlng"][0]
                longitude = store["latlng"][1]
        location_type = "<MISSING>"
        phone = "<INACCESSIBLE>"

        yield [
            locator_domain,
            link,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
