import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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
    scraped_items = []

    DOMAIN = "feederssupply.com"
    start_url = "https://siteassets.parastorage.com/singlePage/viewerViewModeJson?ck=6&commonConfig=%7B%22siteRevision%22%3A%225077%22%7D&experiments=bv_migrateResponsiveToVariantsModels%2Cbv_migrateResponsiveLayoutToSingleLayoutData%2Cdm_removeMissingResponsiveRefs%2Csv_usedFontsDataFixer&isHttps=true&isUrlMigrated=true&metaSiteId=99c3c672-4d0e-4453-bff1-d20c7c343d3a&quickActionsMenuEnabled=false&siteId=a28f0e4c-0aac-4734-b310-f3f04092f1f8&v=3&pageId=3206a6_96a37f415e3bff3c30c79dc07674f5e0_5076&module=viewer-view-mode-json&moduleVersion=1.283.0&viewMode=desktop&siteRevision=5077&dfVersion=1.1187.0"
    response = session.get(start_url)
    data = json.loads(response.text)

    all_elems = [
        elem
        for elem in data["data"]["document_data"].values()
        if elem.get("pageUriSEO")
    ]

    for poi in all_elems:
        store_url = "https://www.feederssupply.com/" + poi["pageUriSEO"]
        if "copy-" not in store_url:
            continue
        if "fish-guarantee" in store_url:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        base_url = (
            "https://www.feederssupply.com/"
            + store_url.split("-of-")[-1].split("-loc")[0]
        )

        final_list = [store_url, base_url]
        for store_url in final_list:
            loc_response = session.get(store_url)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)
            raw_data = loc_dom.xpath(
                '//div[@data-testid="mesh-container-content"]/div[1]//text()'
            )
            raw_data = [e.strip() for e in raw_data if e.strip()]
            if len(raw_data) < 3:
                raw_data = loc_dom.xpath(
                    '//div[@data-testid="mesh-container-content"]/div[3]//text()'
                )
                raw_data = [e.strip() for e in raw_data if e.strip()]
            addr = parse_address_intl(" ".join(raw_data[1:-1]))

            location_name = raw_data[0]
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            city = city if city else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//a[@data-type="phone"]/@data-content')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = loc_dom.xpath(
                '//div[contains(@id,"comp")]/div[@data-packed="true"][2]/p[2]//text()'
            )
            if not hours_of_operation:
                hours_of_operation = loc_dom.xpath(
                    '//*[contains(text(), "00pm")][1]/text()'
                )
            hours_of_operation = [elem.strip() for elem in hours_of_operation]
            hours_of_operation = (
                " ".join(hours_of_operation).replace("  ", " ")
                if hours_of_operation
                else "<MISSING>"
            )
            if "pm Mon." in hours_of_operation:
                hours_of_operation = hours_of_operation.split("pm Mon.")[0] + "pm"

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
            check = location_name.split(",")[0].replace("- ", "")
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
