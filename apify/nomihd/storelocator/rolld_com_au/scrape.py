# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "rolld.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    api_url = "https://rolld.com.au/wp-admin/admin-ajax.php?action=store_search&lat=-25.274398&lng=133.775136&max_results=50000&search_radius=5000&autoload=1"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)
        json_res = json.loads(api_res.text)

        stores = json_res

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = store["permalink"]

            location_name = (
                store["store"]
                .replace("&#8217;", "'")
                .replace("&#8211;", "-")
                .strip()
                .replace("&#038;", "&")
                .strip()
            )

            location_type = "<MISSING>"
            if "Temporarily Closed" in location_name:
                location_type = "Temporarily Closed"
                location_name = location_name.split("-")[0].strip()

            raw_address = "<MISSING>"

            street_address = (store["address"] + store["address2"]).strip(", ").strip()

            city = store["city"]

            state = store["state"]

            zip = store["zip"]

            country_code = store["country"]

            phone = "<MISSING>"

            hour_str = store["hours"]
            hours_of_operation = "<MISSING>"
            if hour_str:
                hours_sel = lxml.html.fromstring(hour_str)

                hours = list(
                    filter(
                        str,
                        [x.strip() for x in hours_sel.xpath("//td//text()")],
                    )
                )
                hours_of_operation = "; ".join(hours).replace("day; ", "day: ")
            else:
                if "extra_data" in store and store["extra_data"]:
                    hours_sel = lxml.html.fromstring(store["extra_data"])

                    hours = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in hours_sel.xpath(
                                    "//div[@class='opening-hours']//li//text()"
                                )
                            ],
                        )
                    )
                    hours_of_operation = (
                        "; ".join(hours)
                        .replace("day; ", "day: ")
                        .strip()
                        .split("Christmas")[0]
                        .strip()
                    )

            store_number = store["id"]

            latitude, longitude = store["lat"], store["lng"]
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

            if page_url:
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                phone = (
                    "".join(store_sel.xpath('//div[@class="phone-number"]/text()'))
                    .strip()
                    .replace("PH:", "")
                    .strip()
                )
                if '"streetAddress": "' in store_req.text:
                    street_address = (
                        store_req.text.split('"streetAddress": "')[1]
                        .strip()
                        .split('",')[0]
                        .strip()
                    )
                    if len(street_address) > 0 and street_address[-1] == ",":
                        street_address = "".join(street_address[:-1]).strip()

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
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
