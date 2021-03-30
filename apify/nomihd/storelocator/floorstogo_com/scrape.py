# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "floorstogo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

url_list = []
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "Origin": "https://www.floorstogo.com",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://www.floorstogo.com/StoreLocator.aspx",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_records_for(zipcode):
    log.info(f"pulling records for zipcode: {zipcode}")
    search_url = (
        "https://www.floorstogo.com/StoreLocator.aspx?&searchZipCode=" + zipcode
    )
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//table[@class="MasterTable_Default"]/tbody/tr')

    yield stores


def process_record(raw_results_from_one_zipcode):
    for stores in raw_results_from_one_zipcode:
        for store in stores:
            page_url = "<MISSING>"
            temp_text = store.xpath(
                ".//div[@class='search-store__results-address col-xs-12 col-sm-4']/p"
            )
            if store.xpath(
                ".//div[@class='search-store__results-address col-xs-12 col-sm-4']"
            ):
                raw_text = []
                for t in temp_text:
                    raw_text.append("".join(t.xpath("text()")).strip())

                locator_domain = website
                location_name = raw_text[-4]
                street_address = raw_text[-3]
                city_state_zip = raw_text[-2]
                city = city_state_zip.split(",")[0].strip()
                state = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[0].strip()
                zip = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[1].strip()

                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                country_code = "US"

                store_number = "<MISSING>"
                phone = raw_text[-1].strip()
                location_type = "<MISSING>"
                hours_of_operation = ""
                web = "".join(
                    store.xpath('.//a[contains(text(),"view website")]/@href')
                ).strip()
                if len(web) > 0:
                    latitude = "<INACCESSIBLE>"
                    longitude = "<INACCESSIBLE>"

                    url = "https://www.floorstogo.com" + web
                    if url not in url_list:
                        url_list.append(url)
                        log.info(url)
                        store_req = session.get(url, headers=headers)
                        store_sel = lxml.html.fromstring(store_req.text)
                        page_url = store_req.url
                        locations = store_sel.xpath('//div[@class="multi-location"]')
                        if len(locations) <= 0:
                            locations = store_sel.xpath(
                                '//div[@class="single-location"]'
                            )
                        hours_of_operation = ""
                        for loc in locations:
                            if (
                                phone
                                == "".join(
                                    loc.xpath('a[@class="footer-phone"]/text()')
                                ).strip()
                            ):
                                hours_of_operation = "".join(
                                    loc.xpath('p[@class="hours"]/text()')
                                ).strip()
                                if not hours_of_operation:
                                    hours_of_operation = "".join(
                                        store_sel.xpath('.//p[@class="hours"]/text()')
                                    ).strip()
                                break
                else:
                    page_url = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"

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
    with SgWriter() as writer:
        results = parallelize(
            search_space=static_zipcode_list(
                radius=200, country_code=SearchableCountries.USA
            ),
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
            max_threads=4,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
