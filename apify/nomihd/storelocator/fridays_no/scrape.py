# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "fridays.no"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://fridays.no/#rest-booking"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="uabb-adv-accordion-item"]')

        for store in stores:

            locator_domain = website
            location_name = "".join(
                store.xpath(".//h4[@class='uabb-adv-accordion-button-label']/text()")
            ).strip()
            page_url = search_url

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            ".//div[@class='uabb-subheading uabb-text-editor']/p/text()"
                        )
                    ],
                )
            )
            if len(store_info) <= 0:
                continue
            raw_address = store_info[0].split(",")
            street_address = raw_address[0].strip()

            city = raw_address[-1].strip().split(" ")[-1].strip()
            state = "<MISSING>"
            zip = raw_address[-1].strip().split(" ")[0].strip()

            country_code = "NO"

            store_number = "<MISSING>"

            phone = store_info[-2].replace("TLF:", "").strip()
            location_type = "<MISSING>"
            hours = store.xpath('.//div[@class="fl-rich-text"]')[-1].xpath(
                'p[@style="text-align: center;"]'
            )
            hours_list = []
            for hour in hours:
                if len("".join(hour.xpath(".//text()")).strip()) > 0:
                    hours_list.append("".join(hour.xpath(".//text()")).strip())

            hours_of_operation = "; ".join(hours_list).strip()
            if len(hours_list) <= 0:
                hours_of_operation = "Mandag- Torsdag  12.00 - 21.00; Fredag -Lørdag  12.00 - 22.00; Søndag   13.00 - 21.00"
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
                raw_address=", ".join(raw_address).strip(),
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
                    SgRecord.Headers.ZIP,
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
