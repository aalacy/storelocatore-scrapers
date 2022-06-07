# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgselenium import SgChrome
import time
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

website = "rapidurgentcare.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def fetch_data():
    # Your scraper here
    base = "https://www.rapidurgentcare.com/"
    search_url = "https://www.rapidurgentcare.com/copy-of-locations-all"

    with SgChrome() as driver:
        driver.get(search_url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight-100);")
        time.sleep(120)
        search_sel = lxml.html.fromstring(driver.page_source)

        raw_text = list(
            filter(
                str,
                search_sel.xpath(
                    '//div[@id="comp-if7uc7zx"]//span[@class="color_19" and not(.//span[@class="wixGuard"])]//text()'
                ),
            )
        )

        store_hours_dict = dict()

        key_start, key_end = 0, 0
        idx = 0
        while idx < len(raw_text):

            key_start = idx
            while "open" not in raw_text[idx].lower():
                idx += 1
            key_end = idx

            key = " ".join(raw_text[key_start:key_end]).lower()
            store_hours_dict[key] = raw_text[key_end : key_end + 2]

            idx = key_end + 2

        store_phones_dict = dict()

        store_names = list(
            filter(
                str,
                search_sel.xpath(
                    '//div[contains(@data-mesh-id,"SITE_FOOTER")]//span[@style="font-style:italic;"]//text()'
                ),
            )
        )

        phone_hrefs = list(
            filter(
                str,
                search_sel.xpath(
                    '//div[contains(@data-mesh-id,"SITE_FOOTER")]//iframe/@src'
                ),
            )
        )

        for idx, store_name in enumerate(store_names, 0):
            phone_res = session.get(phone_hrefs[idx])
            phone_sel = lxml.html.fromstring(phone_res.text)
            phn = "".join(phone_sel.xpath("//a/text()")).strip()

            store_phones_dict[store_name.strip().lower()] = phn

        iframe = driver.find_element_by_xpath('//iframe[@title="Map & Store Locator"]')
        driver.switch_to.frame(iframe)
        time.sleep(40)
        iframe_sel = lxml.html.fromstring(driver.page_source)

        stores_list = iframe_sel.xpath('//ul[contains(@id,"locations")]/li')

        for store in stores_list:
            phone = ""
            page_url = ""
            hours_of_operation = ""
            store_name = "".join(store.xpath(".//a//text()")).strip()
            # check if it maps to store_phones_dict.
            for name in store_phones_dict.keys():
                if name in store_name.lower():
                    page_url = base + name.replace(" ", "").strip()
                    phone = store_phones_dict[name]

                    for key in store_hours_dict.keys():
                        if name in key:
                            hours_of_operation = (
                                " ".join(store_hours_dict[key])
                                .strip()
                                .replace("Open ", "")
                                .strip()
                            )
                            break
                    break

            raw_address = " ".join(store.xpath(".//span//text()")).strip()

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = formatted_addr.country

            location_name = store_name.strip()
            locator_domain = website
            store_number = "<MISSING>"
            location_type = "<MISSING>"

            latitude = store.xpath("./@data-geo-lat")[0].strip()
            longitude = store.xpath("./@data-geo-lng")[0].strip()

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
