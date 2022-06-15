# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "indigohealth.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

session = SgRequests()
headers = {
    "authority": "www.indigohealth.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.indigohealth.com/locations"

    search_res = session.get(search_url, headers=headers)
    markers_dict = json.loads(
        search_res.text.split("const markersData = ")[1].strip().split("}};")[0].strip()
        + "}}"
    )
    search_sel = lxml.html.fromstring(search_res.text)
    stores_list = search_sel.xpath('//div[@id="locations-list"]/div')

    for store in stores_list:

        page_url = (
            "https://www.indigohealth.com"
            + "".join(store.xpath('.//h3[@class="h5"]/a/@href')).strip()
        )
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website

        location_name = "".join(store_sel.xpath("//h1[@class='h3']/text()")).strip()

        store_info = list(
            filter(
                str,
                store_sel.xpath(
                    '//div[@class="col-lg-5 pt-3 d-none d-lg-block"]//address//text()'
                ),
            )
        )
        street_address = store_info[1].strip()
        city = store_info[-1].strip().split(",")[0].strip()
        state = store_info[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()
        zip = store_info[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        phone = "".join(
            store_sel.xpath(
                '//div[@class="col-lg-5 pt-3 d-none d-lg-block"]//li[@class="icon-phone"]/a/text()'
            )
        )

        location_type = "<MISSING>"

        hours = store_sel.xpath('//div[@id="accordion-hours-urgent-care"]//li')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("strong/text()")).strip()
            time = "".join(hour.xpath("text()")).strip()
            hours_list.append(day + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = markers_dict["".join(store.xpath("@data-clinic")).strip()]["coord"][
            "lat"
        ]
        longitude = markers_dict["".join(store.xpath("@data-clinic")).strip()]["coord"][
            "lng"
        ]

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
