# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "fiat.rs"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.fiat.ec",
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
    search_url = "https://www.fiat.rs/spisak-dilera"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        sections = search_sel.xpath(
            '//div[@class="clearfix content-header-fixed"]/div/div[@class="textsection parbase"]'
        )
        location_type = ""
        for section in sections:
            if (
                len(
                    "".join(
                        section.xpath('.//h2[@data-p2c="title(text)"]/text()')
                    ).strip()
                )
                > 0
            ):
                location_type = "".join(
                    section.xpath('.//h2[@data-p2c="title(text)"]/text()')
                ).strip()
            else:
                stores = section.xpath(
                    './/div[@class="col-xs-12 col-sm-6 col-md-3 padding-top-15 single-box-st-purchasing"][./div[1]//h3]'
                )
                for store in stores:
                    page_url = search_url
                    locator_domain = website
                    location_name = "".join(
                        store.xpath("div[1]//h3/strong/text()")
                    ).strip()

                    store_info = store.xpath(".//p/text()")
                    street_address = "".join(store_info[0]).strip()
                    city = "".join(store_info[1]).strip().replace("BiH", "").strip()
                    zip = "<MISSING>"
                    if city == "71 000 Sarajevo":
                        city = "Sarajevo"
                        zip = "71 000"
                    state = "<MISSING>"

                    country_code = "<MISSING>"

                    phone = "<MISSING>"
                    store_number = "<MISSING>"

                    hours_of_operation = "<MISSING>"
                    for info in store_info:
                        if "Radno vreme:" in info:
                            hours_of_operation = info.replace(
                                "Radno vreme:", ""
                            ).strip()
                        if "Telefon:" in info:
                            phone = info.replace("Telefon:", "").strip()
                        if "E-mail:" in info or "@" in info:
                            if ".rs" in info:
                                country_code = "RS"
                            elif ".ba" in info:
                                country_code = "BA"

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
                    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
