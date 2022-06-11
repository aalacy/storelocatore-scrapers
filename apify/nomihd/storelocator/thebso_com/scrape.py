# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "thebso.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = (
        "https://www.thebso.com/content/dam/sitemaps/thebso/sitemap_thebso_en_us.xml"
    )
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("<loc>")
    for index in range(1, len(stores)):
        temp_url = stores[index].split("</loc>")[0].strip()
        if (
            "/locations/" in temp_url
            and len(temp_url.split("/locations/")[1].split("/")) == 3
        ):
            page_url = temp_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_type = "<MISSING>"
            locator_domain = website
            location_name = "".join(
                store_sel.xpath(
                    '//div[@id="main-content"]//div[@class="salondetailspagelocationcomp"]/div/h1[@class="sub-brand"]/text()'
                )
            ).strip()

            street_address = "".join(
                store_sel.xpath(
                    '//div[@id="main-content"]//div[@class="salondetailspagelocationcomp"]//span[@class="store-address"]/span[@itemprop="streetAddress"]/text()'
                )
            ).strip()
            city = "".join(
                store_sel.xpath(
                    '//div[@id="main-content"]//div[@class="salondetailspagelocationcomp"]//span[@class="store-address"]/span[@itemprop="addressLocality"]/text()'
                )
            ).strip()
            state = "".join(
                store_sel.xpath(
                    '//div[@id="main-content"]//div[@class="salondetailspagelocationcomp"]//span[@class="store-address"]/span[@itemprop="addressRegion"]/text()'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//div[@id="main-content"]//div[@class="salondetailspagelocationcomp"]//span[@class="store-address"]/span[@itemprop="postalCode"]/text()'
                )
            ).strip()
            country_code = "CA"
            if us.states.lookup(state):
                country_code = "US"
            phone = "".join(
                store_sel.xpath(
                    '//div[@id="main-content"]//div[@class="salondetailspagelocationcomp"]//span[@itemprop="telephone"]/text()'
                )
            ).strip()

            if phone == "(0) 0-0":
                phone = "<MISSING>"

            hours_of_operation = ""
            hours = store_sel.xpath('//div[@class="salon-timings"]')
            hours_list = []
            if len(hours) > 0:
                hours = hours[0].xpath("span")
                for hour in hours:
                    hours_list.append("".join(hour.xpath("div/text()")).strip())

            hours_of_operation = "; ".join(hours_list).strip()
            store_number = page_url.split("-")[-1].strip().replace(".html", "").strip()
            latlng = store_sel.xpath('//div[@itemprop="geo"]')
            latitude = ""
            longitude = ""
            if len(latlng) > 0:
                latitude = "".join(
                    latlng[0].xpath('meta[@itemprop="latitude"]/@content')
                ).strip()
                longitude = "".join(
                    latlng[0].xpath('meta[@itemprop="longitude"]/@content')
                ).strip()

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
