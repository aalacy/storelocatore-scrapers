# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
import re
import time
import json

website = "lgstoreswv.com"
logger = sglog.SgLogSetup().get_logger(logger_name=website)
DOMAIN = "https://lgstoreswv.com/"

pattern_tag = re.compile(r"<[^>]+>")


def remove_tags(raw_text):
    clean = pattern_tag.sub(":", raw_text)
    clean = clean.split(":")
    clean = [i for i in clean if i]
    return clean


def fetch_data():
    # Your scraper here
    headers = {}
    headers["cookie"] = ""
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    found_in_path = "/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLj4lxTizKLy1OzVHSUcpNLIjPTAEqNVKqBQBtfBRD"
    url_base = "https://lgstoreswv.com/locations/"
    url_data = "https://lgstoreswv.com/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLj4lxTizKLy1OzVHSUcpNLIjPTAEqNVKqBQBtfBRD"
    with SgChrome() as driver:
        driver.get(url_data)
        time.sleep(10)
        for r in driver.requests:
            if found_in_path in r.path:
                try:
                    headers["cookie"] = r.headers["cookie"]
                    logger.info(f'[COOKIE: {headers["cookie"]}]')
                except Exception:
                    try:
                        headers["cookie"] = r.response.headers["cookie"]
                    except Exception:
                        headers["cookie"] = headers["cookie"]

        driver.get(url_data)
        time.sleep(10)
        response_data = driver.find_element_by_tag_name("body").text
        data_stores = json.loads(response_data)["meta"]
    HOO = "<MISSING>"
    for idx, data in enumerate(data_stores):
        page_url = url_base
        locator_domain = website
        store_description1 = remove_tags(data["description"])
        store_description = []
        if len(store_description1) > 3:
            for idx1, v in enumerate(store_description1):
                if idx1 == 0:
                    store_description.append(v)
                if idx1 == 1:
                    store_description.append(
                        store_description1[1] + store_description1[2]
                    )
                if idx1 == 3:
                    store_description.append(v)
        else:
            for idx1, v in enumerate(store_description1):
                store_description.append(v)
        location_name = store_description[0] if store_description[0] else "<MISSING>"
        address_data = store_description[1]
        address_data = address_data.replace("Avenue, SW", "Avenue SW").replace(
            "Rd - Hunting", "Rd, Hunting"
        )
        street_address = (
            address_data.split(",")[0].strip() if address_data else "<MISSING>"
        )
        try:
            city = address_data.split(",")[1].strip()
        except:
            city = "<MISSING>"
        state = (
            address_data.split(",")[-1][:-5].strip() if address_data else "<MISSING>"
        )
        zip = address_data.rsplit(" ", 1)[1] if address_data else "<MISSING>"
        country_code = "US"
        store_number = (
            location_name.split("#")[1].strip() if location_name else "<MISSING>"
        )
        try:
            phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", str(store_description[2]))[0]
        except:
            phone = "<MISSING>"
        location_type = data["icon"].split("/")[-1].split("-MapIcon")[0].strip()
        latitude = data["lat"]
        longitude = data["lng"]
        if city == "Lic":
            street_address = street_address + " " + city
            city = "<MISSING>"
        hours_of_operation = HOO

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
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
