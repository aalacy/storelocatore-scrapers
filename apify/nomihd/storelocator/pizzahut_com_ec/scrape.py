# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "pizzahut.com.ec"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.pizzahut.com.ec"
    search_url = "https://www.pizzahut.com.ec/pizzerias"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    states = search_sel.xpath('//ul[@class="areas"]/li/a')

    for stat in states:
        state = "".join(stat.xpath("text()")).strip()
        state_url = base + "".join(stat.xpath("@href")).strip()

        state_req = session.get(state_url, headers=headers)
        state_sel = lxml.html.fromstring(state_req.text)
        cities = state_sel.xpath('//ul[@class="cities"]/li/a')
        for cty in cities:
            city = "".join(cty.xpath("text()")).strip()
            city_url = base + "".join(cty.xpath("@href")).strip()
            stores_req = session.get(city_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//div[@class="mod_store_address"]/ul/li//a[@class="moreInfoLinkFromList"]/@href'
            )
            for store_url in stores:
                page_url = base + store_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                locator_domain = website
                location_name = "".join(
                    store_sel.xpath(
                        '//div[@class="mod_generic_promotion shopTitle"]/h1/text()'
                    )
                ).strip()

                street_address = "".join(
                    store_sel.xpath("//address/span[1]/text()")
                ).strip()
                zip = "".join(store_sel.xpath("//address/span[2]/text()")).strip()
                country_code = "EC"

                phone = "".join(
                    store_sel.xpath('//span[@itemprop="telephone"]/a/text()')
                ).strip()
                store_number = page_url.split("-")[-1].strip()

                location_type = "<MISSING>"

                hours = store_sel.xpath(
                    '//div[@class="hours clearfix pls prs pbs mts"]/div[1]/table//tr'
                )
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("td[1]/text()")).strip()
                    time = "".join(hour.xpath("td[2]/text()")).strip()
                    hours_list.append(day + ": " + time)

                hours_of_operation = "; ".join(hours_list).strip()

                latitude = (
                    store_req.text.split("var lat = ")[1].strip().split(";")[0].strip()
                )
                longitude = (
                    store_req.text.split("var lng = ")[1].strip().split(";")[0].strip()
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
