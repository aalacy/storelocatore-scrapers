# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "papajohns.ae"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.papajohns.ae/pj/find-restaurants"
    with SgRequests(dont_retry_status_codes=set([404]), verify_ssl=False) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        markers = search_sel.xpath("//markers/marker")
        store_list = search_sel.xpath('//ul[@id="storeresult"]/li')

        for index in range(0, len(store_list)):
            page_url = search_url
            store_info = ",".join(store_list[index].xpath("p/text()"))
            locator_domain = website
            location_name = "".join(markers[index].xpath("@name")).strip()
            street_address = (
                "".join(markers[index].xpath("@address")).strip().replace("&#39;", "'")
            )
            city = street_address.split(",")[1].strip()
            if city == "UAE":
                city = "<MISSING>"

            street_address = street_address.split(",")[0].strip()
            state = "<MISSING>"
            zip = "<MISSING>"
            country_code = "AE"

            store_number = "<MISSING>"
            phone = "<MISSING>"
            try:
                phone = store_info.split("Tel:")[1].strip().split("Call")[0].strip()
            except:
                phone = store_info.split("Call")[1].strip().split(",")[0].strip()

            if "/" in phone:
                phone = phone.split("/")[0].strip()

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            try:
                hours_of_operation = store_list[index].xpath(
                    'p[./strong[contains(text(),"Delivery:")]]/text()'
                )[-1]
            except:
                pass

            latitude = "".join(markers[index].xpath("@lat")).strip()
            longitude = "".join(markers[index].xpath("@lng")).strip()

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
