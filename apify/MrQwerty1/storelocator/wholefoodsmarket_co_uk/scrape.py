from sgrequests import SgRequests
from lxml import html
from sglogging import SgLogSetup
import json
import csv

logger = SgLogSetup().get_logger(logger_name="wholefoodsmarket_co_uk")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    locator_domain = "https://www.wholefoodsmarket.co.uk/"

    url_json_data_src = "https://www.wholefoodsmarket.co.uk/staticData/"

    session = SgRequests()
    res = session.get(locator_domain)
    data_raw = html.fromstring(res.text, "lxml")
    get_the_code_local = data_raw.xpath('//script[@type="text/javascript"]/text()')[0]
    get_the_code_local = get_the_code_local.split("window.__routeData = ")[1].split(
        ";"
    )[0]
    get_the_code_local = json.loads(get_the_code_local)["propsMap"]["__local"]
    url_json_data_src_built = f"{url_json_data_src}{get_the_code_local}.json"
    r = session.get(url_json_data_src_built)
    js = r.json()["siteData"]["stores"]
    logger.info(f"Pulling the Data From {url_json_data_src_built}")
    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        country_code = "GB"
        store_number = "<MISSING>"
        page_url = f'https://www.wholefoodsmarket.co.uk/stores/{j.get("folder")}'
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        loc = j.get("geo_location").get("coordinates")
        latitude = loc[1] or "<MISSING>"
        longitude = loc[0] or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    logger.info("Scraping Started")
    data = fetch_data()
    logger.info(f"Scraping Finished | Total Store Count:{len(data)}")
    write_output(data)


if __name__ == "__main__":
    scrape()
