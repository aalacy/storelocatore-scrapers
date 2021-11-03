# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "chavezsuper.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.chavezsuper.com/about"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath(
        '//div[contains(@class,"wrapperDiv_1oj30as") and .//h2[contains(@class,"heading")]]'
    )

    for store in store_list:

        page_url = search_url
        locator_domain = website

        location_name = " ".join(
            list(
                filter(
                    str,
                    store.xpath(
                        './p[(./following-sibling::div[./p]) and (./preceding-sibling::a[contains(@data-event,"get-directions")]) ]//text()'
                    ),
                )
            )
        ).strip()
        address_info = list(
            filter(
                str,
                store.xpath("./div[./p]//text()"),
            )
        )

        address_info = list(filter(str, ([x.strip() for x in address_info])))
        street_address = " ".join(address_info[0:-1]).strip()

        city = address_info[-1].split(",")[0].strip()

        state = (
            "".join(address_info[-1].split(",")[1:]).strip().split(" ")[0].strip(" ,")
        )
        zip = "".join(address_info[-1].split(",")[1:]).strip().split(" ")[1].strip(" ,")

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(store.xpath("./div[./a[@href]]//text()")).strip()

        location_type = "<MISSING>"

        hours_info = list(
            filter(str, store.xpath("./div[not(./p or ./a) and text()]//text()"))
        )
        hours_info = list(filter(str, [x.strip() for x in hours_info]))

        hours_of_operation = ": ".join(hours_info)

        lat_lng_href = "".join(store.xpath('./a[contains(@href,"maps")]/@href'))

        if "z/data" in lat_lng_href:
            lat_lng = lat_lng_href.split("@")[1].split("z/data")[0]
            latitude = lat_lng.split(",")[0].strip()
            longitude = lat_lng.split(",")[1].strip()
        elif "ll=" in lat_lng_href:
            lat_lng = lat_lng_href.split("ll=")[1].split("&")[0]
            latitude = lat_lng.split(",")[0]
            longitude = lat_lng.split(",")[1]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        raw_address = "<MISSING>"
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
