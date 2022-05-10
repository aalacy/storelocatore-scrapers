# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "tgifridaysbrasil.com.br"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.tgifridaysbrasil.com.br",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.tgifridaysbrasil.com.br/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="info"]')
        for store in stores:
            page_url = search_url
            location_name = "".join(store.xpath("h5/text()")).strip()
            locator_domain = website

            raw_address = (
                ", ".join(
                    store.xpath(
                        'div[@class="endereco"]/p[./strong[contains(text(),"Endere")]]/text()'
                    )
                )
                .strip()
                .split(",")
            )
            street_address = ", ".join(raw_address[:2]).strip()
            city = ""
            state = ""
            zip = raw_address[-1].strip()
            if zip.replace("-", "").strip().isdigit():
                city = raw_address[-2].strip().split("-")[0].strip()
                state = raw_address[-2].strip().split("-")[1].strip()
            else:
                city = raw_address[-1].strip().split("/")[0].strip()
                state = raw_address[-1].strip().split("/")[1].strip()
                zip = "<MISSING>"

            if "SP1089" in state:
                state = "SP"
                zip = "1089"

            country_code = "BR"

            phone = "".join(
                store.xpath(
                    'div[@class="endereco"]/p[./strong[contains(text(),"Tel:")]]/text()'
                )
            ).strip()
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = (
                "; ".join(
                    store.xpath(
                        'div[@class="endereco"]/p[./strong[contains(text(),"rio de funcionamento:")]]/text()'
                    )
                )
                .strip()
                .split("Delivery")[0]
                .strip()
            )

            if ";" == hours_of_operation[-1]:
                hours_of_operation = "".join(hours_of_operation[:-1]).strip()

            if "Em breve reabertura" in hours_of_operation:
                location_type = "Temporarily Closed"
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
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
