# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "mauitacos.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "mauitacos.com",
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
    search_url = "https://mauitacos.com/locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    area_list = search_sel.xpath('//div//div[@class="wpb_wrapper" and (./h3)]')[:-1]

    for area in area_list:
        store_names = list(
            filter(
                str,
                [x.strip() for x in area.xpath("./*[self::h3]//text()")],
            )
        )
        for pos, store_name in enumerate(store_names, 1):  # pos is position

            page_url = search_url
            locator_domain = website
            location_name = store_name
            store_number = "<MISSING>"
            location_type = "<MISSING>"

            raw_info = area.xpath(
                f'./p[(count(preceding-sibling::h2)={pos} or count(preceding-sibling::h3)={pos}) and not(contains(.//a//text(),"Menu"))]/text()'
            )
            add_list = []
            phone = "<MISSING>"
            for info in raw_info:
                if "Phone" in info:
                    phone = "".join(info).strip().replace("Phone:", "").strip()
                    break
                else:
                    add_list.append("".join(info).strip())

            street_address = (
                ", ".join(add_list[:-1]).strip().split("Shopping Center,")[-1].strip()
            )
            city_state_zip = "".join(add_list[-1]).strip()

            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
