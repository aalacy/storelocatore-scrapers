# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "childtime.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    with SgRequests() as session:
        locations_resp = session.get(
            "https://www.childtime.com/sitemaps/www-childtime-com-schools.xml/",
            headers=headers,
        )
        stores = locations_resp.text.split("<loc>")
        for index in range(1, len(stores)):
            page_url = stores[index].split("</loc>")[0].strip()
            log.info(page_url)
            store_resp = session.get(
                page_url,
                headers=headers,
            )
            store_sel = lxml.html.fromstring(store_resp.text)

            json_temp = store_sel.xpath('//script[@type="application/ld+json"]/text()')
            for js in json_temp:
                if "streetAddress" in js:
                    store_json = json.loads(js)
                    location_name = store_json["name"]
                    street_address = store_json["address"]["streetAddress"]
                    city = store_json["address"]["addressLocality"]
                    state = store_json["address"]["addressRegion"]

                    zip = store_json["address"]["postalCode"]

                    latitude = "".join(
                        store_sel.xpath(
                            '//a[@class="show-map"]'
                            '/span[@class="addr"]/@data-latitude'
                        )
                    )
                    longitude = "".join(
                        store_sel.xpath(
                            '//a[@class="show-map"]'
                            '/span[@class="addr"]/@data-longitude'
                        )
                    )

                    if us.states.lookup(state):
                        country_code = "US"

                    store_number = "".join(
                        store_sel.xpath(
                            '//div[@class="school-info"]' "/@data-school-id"
                        )
                    ).strip()
                    phone = "".join(
                        store_sel.xpath('//span[@class="localPhone"]/text()')
                    ).strip()
                    if len(phone) <= 0:
                        phone = "".join(
                            store_sel.xpath(
                                '//div[@class="school-info-row vcard"]//span[@class="tel"]/text()'
                            )
                        ).strip()
                    hours_of_operation = store_json["openingHours"]

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
