# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "burrislogistics.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.burrislogistics.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.burrislogistics.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    sections = stores_sel.xpath('//ul[@class="locations-list__items"]')[:-1]
    for sec in sections:
        stores = sec.xpath("li/a/@href")
        for store_url in stores:
            page_url = store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website

            location_name = " ".join(
                store_sel.xpath('//div[@class="et_pb_text_inner"]//h1/text()')
            ).strip()

            add_sections = store_sel.xpath('//div[@class="et_pb_text_inner"]')
            add_list = []
            phone = ""
            for add in add_sections:
                if "Address" in "".join(add.xpath("h4/text()")).strip():
                    address = add.xpath("p[1]/text()")
                    phone = "".join(
                        add.xpath('p[1]//a[contains(@href,"tel:")]/text()')
                    ).strip()
                    if len(phone) <= 0:
                        phone = "".join(
                            add.xpath('.//span[@style="font-weight: 400;"]/text()')
                        ).strip()
                    add_list = []
                    for add in address:
                        if len("".join(add).strip()) > 0 and (
                            "Phone" not in "".join(add).strip()
                            and "Fax" not in "".join(add).strip()
                        ):
                            add_list.append("".join(add).strip())

                        if len(phone) <= 0:
                            if "Phone" in "".join(add).strip():
                                phone = (
                                    "".join(add).strip().replace("Phone:", "").strip()
                                )

                    break

            street_address = add_list[0].strip()
            city = add_list[-1].strip().split(",")[0].strip()
            state_zip = add_list[-1].strip().split(",")[-1].strip().split(" ")
            state = "<MISSING>"
            zip = "<MISSING>"
            if len(state_zip) > 1:
                state = state_zip[0].strip()
                zip = state_zip[-1].strip()
            else:
                state = state_zip[0].strip()

            country_code = "US"

            store_number = "<MISSING>"

            if len(phone) <= 0:
                phone = "".join(store_sel.xpath('//a[@class="callnow"]/text()')).strip()
                if len(phone) <= 0:
                    phone = "".join(
                        store_sel.xpath('//a[@class="callpill"]/text()')
                    ).strip()

            phone = phone.split("/")[0].strip()
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            map_link = "".join(
                store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
            ).strip()

            if len(map_link) > 0:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
