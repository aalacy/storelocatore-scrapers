# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "sportsfevercal.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.sportsfevercal.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.zip-codes.com/storelocator/serve-store.asp?apikey=V2PRCAPY5SHWTGKOOOTL&zip=95605&map_frame_col=%2328285e&map_height=0&list_limit=2000&max_pages=2&store_col=%2328285e&result_col=%23333333&force_layout=horizontal&width=100%25&height=502&explicitstyle=true&jsopen=true&PG=1"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        store_list = search_sel.xpath('//div[contains(@id,"slResults")]/div')

        for store in store_list[:-1]:

            page_url = "https://www.sportsfevercal.com/store-locator/"

            locator_domain = website

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath("./input/@value")],
                )
            )

            full_address = " ".join(store_info)

            street_address = (
                ",".join(full_address.split(",")[:-3])
                .strip()
                .replace("Arden Fair Mall", "")
                .strip()
                .replace("Roseville Galleria Mall", "")
                .strip()
                .replace("Folsom Outlets", "")
                .strip()
                .replace("Chico Mall", "")
                .strip()
                .replace("The Pruneyard", "")
                .strip()
                .replace("Oakridge Mall", "")
                .strip()
                .replace("Mt. Shasta Mall", "")
                .strip()
                .replace("Parkway Plaza ", "")
                .strip()
                .replace("Plaza Bonita Mall", "")
                .strip()
            )
            city = full_address.split(",")[-3].strip()
            state = full_address.split(",")[-2].strip()
            zip = full_address.split(",")[-1].strip()
            country_code = "US"

            location_name = (
                "".join(store.xpath('./div[@class="resName"]/a/text()'))
                .strip("1234567890 ")
                .strip()
            )
            phone = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath('.//div[contains(@id,"a")]//text()')
                    ],
                )
            )
            phone = (
                " ".join(phone)
                .split("Phone:")[1]
                .split("Fax")[0]
                .split("Get Directions")[0]
                .strip()
            )

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude, longitude = (
                "".join(store.xpath('.//div[contains(@id,"custom02")]/text()')),
                "".join(store.xpath('.//div[contains(@id,"custom03")]/text()')),
            )

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
