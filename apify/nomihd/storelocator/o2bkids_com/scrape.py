# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import sglog
import lxml.html
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "o2bkids.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.o2bkids.com/company-overview/find-a-location/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="locations"]/ul/li')
    for store in stores:
        if "coming soon" not in "".join(store.xpath("h2/a/text()")).strip().lower():
            page_url = "".join(store.xpath("h2/a/@href")).strip()
            locator_domain = website
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_name = (
                "".join(
                    store_sel.xpath(
                        '//h1[@class="t-center hero-title-size purple"]/text()'
                    )
                )
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            address = ""
            phone = ""
            hours = ""
            add_list = []
            sections = store_sel.xpath('//div[contains(@class,"address-list")]/div')
            for sec in sections:
                if (
                    "Address"
                    in "".join(
                        sec.xpath('span[@class="main-p-size list-title"]/strong/text()')
                    ).strip()
                ):
                    address = sec.xpath('span[@class="main-p-size"][1]//text()')
                    for add in address:
                        if len("".join(add).strip()) > 0:
                            add_list.append("".join(add).strip())

                if (
                    "Phone Numbers"
                    in "".join(
                        sec.xpath('span[@class="main-p-size list-title"]/strong/text()')
                    ).strip()
                ):
                    phone = sec.xpath('span[@class="main-p-size"][1]//text()')[
                        0
                    ].strip()

                if (
                    "Hours"
                    in "".join(
                        sec.xpath('span[@class="main-p-size list-title"]/strong/text()')
                    ).strip()
                ):
                    log.info("Present")
                    hours = sec.xpath("div")

            if len(add_list) > 1:
                street_address = ", ".join(add_list[:-1]).strip()
                city = add_list[-1].split(",")[0].strip()
                state = add_list[-1].split(",")[-1].strip().split(" ")[0].strip()
                zip = add_list[-1].split(",")[-1].strip().split(" ")[-1].strip()

            else:
                temp_address = "".join(address).strip()
                street_address = ", ".join(temp_address.rsplit(",")[:-2]).strip()
                city = temp_address.rsplit(",")[-2].strip()
                state = temp_address.rsplit(",")[-1].strip().split(" ")[0].strip()
                zip = temp_address.rsplit(",")[-1].strip().split(" ")[-1].strip()

            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            store_number = "<MISSING>"

            location_type = "<MISSING>"
            hour_list = []
            hours = store_sel.xpath('//div[contains(@class,"hours")]/div')
            for hour in hours:
                hour_list.append(
                    "".join(list(filter(str, hour.xpath("./span//text()"))))
                )

            hours_of_operation = "; ".join(hour_list).strip()

            latitude = "".join(
                store_sel.xpath('//div[@class="marker"]/@data-lat')
            ).strip()
            longitude = "".join(
                store_sel.xpath('//div[@class="marker"]/@data-lng')
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
