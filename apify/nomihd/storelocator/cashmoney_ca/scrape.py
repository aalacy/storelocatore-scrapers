# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "cashmoney.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "*/*",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "content-type": "application/json",
    "Origin": "https://www.cashmoney.ca",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.cashmoney.ca/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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
    search_url = "https://www.curo.com/Cobra/"
    data = {
        "operationName": "getStores",
        "variables": {"brands": ["CASHMONEY"]},
        "query": "query getStores($brands: [Brands!]) {\n  stores(where: {brand_in: $brands}) {\n    edges {\n      node {\n        id\n        city {\n          id\n          name\n          urlSafeName\n          state {\n            id\n            name\n            urlSafeName\n            __typename\n          }\n          __typename\n        }\n        disabledAt\n        brand\n        url\n        temporarilyClosed\n        storeOpenDate\n        disabledAt\n        hours\n        gPS\n        crossStreets\n        title\n        metaDescription\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
    }

    stores_req = session.post(search_url, json=data, headers=headers)
    stores = json.loads(stores_req.text)["data"]["stores"]["edges"]
    for store in stores:
        location_name = store["node"]["title"]

        locator_domain = website
        latitude = store["node"]["gPS"].split(",")[0].strip()
        longitude = store["node"]["gPS"].split(",")[1].strip()

        store_number = str(store["node"]["id"])
        location_type = "<MISSING>"
        if store["node"]["temporarilyClosed"] is True:
            location_type = "temporarilyClosed"

        city = store["node"]["city"]["name"]
        state = store["node"]["city"]["state"]["name"]
        hours_of_operation = store["node"]["hours"]

        page_url = (
            "https://www.cashmoney.ca/find-a-store/"
            + store["node"]["city"]["state"]["urlSafeName"]
            + "/"
            + store["node"]["city"]["urlSafeName"]
            + "/"
            + store["node"]["url"]
        )
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        if store_req.ok is False:
            continue
        zip = ""
        street_address = ""

        store_json = json.loads(
            "".join(
                store_sel.xpath('//script[@type="application/ld+json"]/text()')
            ).strip()
        )
        street_address = store_json["address"]["streetAddress"]
        zip = store_json["address"]["postalCode"]

        phone = store_json["telephone"]

        country_code = "CA"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
