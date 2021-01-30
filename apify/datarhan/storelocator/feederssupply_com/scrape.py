import csv
import json
from lxml import etree

from sgrequests import SgRequests


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
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "feederssupply.com"
    start_url = "https://siteassets.parastorage.com/singlePage/viewerViewModeJson?ck=6&commonConfig=%7B%22siteRevision%22%3A%225077%22%7D&experiments=bv_migrateResponsiveToVariantsModels%2Cbv_migrateResponsiveLayoutToSingleLayoutData%2Cdm_removeMissingResponsiveRefs%2Csv_usedFontsDataFixer&isHttps=true&isUrlMigrated=true&metaSiteId=99c3c672-4d0e-4453-bff1-d20c7c343d3a&quickActionsMenuEnabled=false&siteId=a28f0e4c-0aac-4734-b310-f3f04092f1f8&v=3&pageId=3206a6_96a37f415e3bff3c30c79dc07674f5e0_5076&module=viewer-view-mode-json&moduleVersion=1.283.0&viewMode=desktop&siteRevision=5077&dfVersion=1.1187.0"
    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in [
        elem
        for elem in data["data"]["document_data"].values()
        if elem.get("pageTitleSEO")
    ]:
        store_url = "https://www.feederssupply.com/" + poi["pageUriSEO"]
        if "copy-of-" in store_url:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        print(store_url)
        raw_data = loc_dom.xpath("//div[@data-packed]//p/span//text()")
        if not loc_dom.xpath('//h2[span[contains(text(), "Feeders Supply -")]]'):
            continue

        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = raw_data[0].strip()
        street_address = street_address if street_address else "<MISSING>"
        city = raw_data[1].split(", ")[0].strip()
        state = raw_data[1].split(", ")[-1].split()[0].strip()
        zip_code = raw_data[1].split(", ")[-1].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[2].strip()
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = raw_data[4].strip()

        item = [
            DOMAIN,
            store_url,
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
