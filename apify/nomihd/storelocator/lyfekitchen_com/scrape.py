# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "lyfekitchen.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.lyfekitchen.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.lyfekitchen.com/location/none/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.lyfekitchen.com/"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        store_list = list(search_sel.xpath('//div[@id="SubMenu-5"]/ul/li'))

        for store in store_list:

            page_url = (
                "https://www.lyfekitchen.com" + "".join(store.xpath("a/@href")).strip()
            )
            locator_domain = website

            location_name = "".join(store.xpath("a/text()")).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            raw_address = store_sel.xpath(
                '//section[@id="intro"]/p[1]/a[@data-bb-track-category="Address"]/text()'
            )
            street_address = raw_address[0].strip()
            if "," == street_address[-1]:
                street_address = "".join(street_address[:-1]).strip()

            city_state_zip = raw_address[-1].strip()
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath(
                    '//section[@id="intro"]/p[1]/a[@data-bb-track-category="Phone Number"]/text()'
                )
            )

            location_type = "<MISSING>"

            hours = store_sel.xpath(
                '//section[@id="intro"]/p[position()>1 and position()<=3]'
            )
            hours_list = []
            for hour in hours:
                hours_list.append(":".join(hour.xpath(".//text()")).strip())

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .replace("LOCATED DIRECTLY INSIDE THE EQUINOX LOBBY;", "")
                .strip()
            )

            latitude, longitude = (
                "".join(store_sel.xpath("//div[@data-gmaps-lng]/@data-gmaps-lat")),
                "".join(store_sel.xpath("//div[@data-gmaps-lng]/@data-gmaps-lng")),
            )

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
