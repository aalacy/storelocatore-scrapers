# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "columbiasportswear.ph"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.columbiasportswear.ph",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.columbiasportswear.ph/cms/7/stores"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        sections = search_sel.xpath(
            '//div[@class="col-xs-12 col-sm-12 col-md-3 app-wrp-adv-stores-section"]'
        )
        for section in sections:
            state = "".join(section.xpath("h5/text()")).strip()
            stores = section.xpath('.//ul[@class="app-lsu-adv-stores-unit"]')

            for store in stores:

                page_url = search_url

                locator_domain = website

                location_name = "".join(store.xpath("li/text()")).strip()

                raw_address = ", ".join(
                    store.xpath("ul[@class='app-lsu-adv-stores-address']/li[1]/text()")
                ).strip()

                street_address = raw_address
                city = "<MISSING>"
                if "city" in raw_address.split(",")[-1].strip().lower():
                    street_address = ", ".join(raw_address.split(",")[:-1]).strip()
                    city = raw_address.split(",")[-1].strip()

                if (
                    city
                    == "2014A 2nd Level Festival Supermall Corporate Ave Filinvest Corporation City Alabang"
                ):
                    street_address = "2014A 2nd Level Festival Supermall Corporate Ave Filinvest Corporation"
                    city = "Alabang"

                zip = "<MISSING>"
                if city.split(" ")[-1].strip().isdigit():
                    zip = city.split(" ")[-1].strip()
                    city = " ".join(city.split(" ")[:-1]).strip()

                country_code = "PH"

                store_number = "<MISSING>"

                phone = "".join(
                    store.xpath("ul[@class='app-lsu-adv-stores-address']/li[2]/text()")
                ).strip()

                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"
                latitude, longitude = "<MISSING>", "<MISSING>"

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
