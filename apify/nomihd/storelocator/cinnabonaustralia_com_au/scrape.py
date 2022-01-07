# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "cinnabonaustralia.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "cinnabonaustralia.com.au",
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
    search_url = "https://cinnabonaustralia.com.au/bakery-locations/"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        store_list = search_sel.xpath('//div[@class="uncont"][.//h4]')

        for store in store_list:

            page_url = search_url

            locator_domain = website

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//div[h5 and h4]//text()")],
                )
            )
            raw_address = (
                ", ".join(store_info)
                .strip()
                .split("Trading Hours")[0]
                .strip()
                .replace("Westfield Southland (near Coles),", "")
                .strip()
                .replace("The Kitchens, Robina Town Centre.,", "")
                .strip()
                .replace("Outside Coles.,", "")
                .strip()
                .replace("Level 2, next to Michael Hill.,", "")
                .strip()
                .replace("Level 1,", "")
                .strip()
                .replace("Opposite Coles.,", "")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            if not city:
                city = raw_address.split(",")[1].strip().split(" ")[0].strip()

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "AU"

            location_name = " ".join(store.xpath(".//h2//text()")).strip()

            phone = " ".join(
                store.xpath('.//*[contains(@href,"tel:")]//text()')
            ).strip()
            store_number = "<MISSING>"

            location_type = "<MISSING>"
            hours_of_operation = (
                "; ".join(store_info)
                .strip()
                .split("Trading Hours")[1]
                .strip()
                .replace(":;", ":")
                .replace("day", "day:")
                .strip()
            )
            try:
                if ";" == hours_of_operation[0]:
                    hours_of_operation = "".join(hours_of_operation[2:]).strip()
            except:
                pass

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.STATE,
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
