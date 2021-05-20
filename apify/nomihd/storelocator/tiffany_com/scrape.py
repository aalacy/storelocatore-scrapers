# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "tiffany.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    countries_req = session.get(
        "https://www.tiffany.com/jewelry-stores/store-list/", headers=headers
    )
    countries_sel = lxml.html.fromstring(countries_req.text)
    countries = countries_sel.xpath(
        '//ul[@class="stores-filter__regions-content-dropdown-list"]/li/a/@href'
    )
    for country_url in countries:
        search_url = "https://www.tiffany.com/" + country_url
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="store-list__store-item"]/a[@class="cta"]/@href'
        )
        for store_url in stores:
            page_url = "https://www.tiffany.com" + store_url
            locator_domain = website
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zip = ""
            store_number = "<MISSING>"
            phone = ""
            location_type = "<MISSING>"
            latitude = ""
            longitude = ""
            hours_of_operation = ""

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
            for js in json_list:
                if "Store" == json.loads(js)["@type"]:
                    json_data = json.loads(js)
                    location_name = json_data["name"]
                    street_address = json_data["address"]["streetAddress"]
                    city = json_data["address"]["addressLocality"]
                    state = json_data["address"]["addressRegion"]
                    zip = json_data["address"]["postalCode"]
                    country_code = json_data["address"]["addressCountry"]
                    phone = json_data["telephone"]
                    map_link = json_data["hasMap"]
                    location_type = json_data["brand"]
                    try:
                        latitude = (
                            map_link.split("sll=")[1].strip().split(",")[0].strip()
                        )
                        longitude = (
                            map_link.split("sll=")[1]
                            .strip()
                            .split(",")[1]
                            .strip()
                            .replace("'", "")
                            .strip()
                        )
                    except:
                        pass

                    if "permanently closed" in json_data["openingHours"]:
                        hours_of_operation = "permanently closed"
                    elif "temporarily closed" in json_data["openingHours"]:
                        hours_of_operation = "temporarily closed"
                    else:
                        temp_hours = json_data["openingHours"]
                        try:
                            if len(temp_hours.split("<br><br>")) == 3:
                                hours_of_operation = (
                                    temp_hours.split("<br><br>")[-1]
                                    .replace("<br>", "; ")
                                    .strip()
                                )
                            else:
                                hours_of_operation = json_data[
                                    "specialOpeningHoursSpecification"
                                ].strip()
                                try:
                                    hours_of_operation = (
                                        hours_of_operation.split("<br><br>")[1]
                                        .replace("<br>", "; ")
                                        .strip()
                                    )
                                except:
                                    pass
                        except:
                            pass

                    try:
                        hours_of_operation = hours_of_operation.split("; Holidays: ")[
                            0
                        ].strip()
                    except:
                        pass

                    hours_of_operation = hours_of_operation.replace(
                        " <br>", "; "
                    ).strip()
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
