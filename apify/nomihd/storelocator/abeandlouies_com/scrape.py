# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "abeandlouies.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "abeandlouies.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://abeandlouies.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://abeandlouies.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores_json = json.loads(
        stores_sel.xpath('//script[@type="application/ld+json"]/text()')[1]
    )

    addresses = stores_json["address"]
    phone_list = stores_json["telephone"]
    coordinates = stores_json["geo"]
    temp_add = "".join(
        stores_sel.xpath('//div[@class="bot-loc-half"]/p/text()')
    ).strip()
    for index in range(0, len(addresses)):
        page_url = search_url

        locator_domain = website

        street_address = addresses[index]["streetAddress"]
        city = addresses[index]["addressLocality"]
        state = addresses[index]["addressRegion"]
        zip = addresses[index]["postalCode"]
        location_name = city + ", " + state
        country_code = "US"

        store_number = "<MISSING>"

        phone = phone_list[index]

        location_type = "<MISSING>"
        hours_of_operation = ""
        if city in temp_add:
            temp_hours = stores_sel.xpath('//p[@class="hours"]/text()')
            hours_list = []
            for hour in temp_hours:
                if (
                    "Temporary Hours" not in "".join(hour).strip()
                    and len("".join(hour).strip()) > 0
                ):
                    hours_list.append("".join(hour).strip())

            hours_of_operation = "; ".join(hours_list).strip()
        else:
            try:
                hours_sel = lxml.html.fromstring(
                    stores_req.text.split(
                        "<!-- Commenting this out to give the proper design <p>"
                    )[-1]
                    .strip()
                    .split("</p>-->")[0]
                    .strip()
                )
                hours_of_operation = (
                    "; ".join(
                        list(
                            filter(str, hours_sel.xpath('//p[@class="hours"]//text()'))
                        )
                    )
                    .strip()
                    .replace("day;", "day:")
                )
            except:
                pass

        latitude = coordinates[index].split(",")[0].strip()
        longitude = coordinates[index].split(",")[-1].strip()

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
