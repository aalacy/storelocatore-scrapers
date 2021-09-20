# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import cloudscraper
import us

website = "umms.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.umms.org",
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


def split_fulladdress(address_info):
    street_address = " ".join(address_info[0:-1]).strip(" ,.")

    city_state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = " ".join(city_state_zip.split(" ")[:-2]).strip()
    state = city_state_zip.split(" ")[-2].strip()
    zip = city_state_zip.split(" ")[-1].strip()

    if not city or us.states.lookup(zip):
        city = city + " " + state
        state = zip
        zip = "<MISSING>"

    if us.states.lookup(state):
        country_code = "US"

    return street_address, city, state, zip, country_code


def fetch_data():
    # Your scraper here
    with SgRequests(dont_retry_status_codes=([404]), verify_ssl=False) as session:
        scraper = cloudscraper.create_scraper(sess=session)
        search_url = "https://www.umms.org/locations"
        search_res = scraper.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        service_list = search_sel.xpath("//option")
        for service in service_list:
            log.info("".join(service.join("./value")))
            service_val = "".join(service.join("./value"))

            service_url = f"https://www.umms.org/locations?perpage=50&serv={service_val}&view=list&st=Locations"
            service_res = scraper.get(service_url, headers=headers)
            service_sel = lxml.html.fromstring(service_res.text)

            store_list = search_sel.xpath('//section[@aria-label="search results"]//li')

            for store in store_list:

                page_url = store.xpath(".//a/@href")[0].strip()

                locator_domain = website

                log.info(page_url)
                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                store_info = list(
                    filter(
                        str,
                        [x.strip() for x in store.xpath(".//address//text()")],
                    )
                )

                raw_address = "<MISSING>"

                street_address, city, state, zip, country_code = split_fulladdress(
                    full_address
                )

                location_name = store.xpath(".//a/text()")[0].strip()

                phone = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath('.//a[contains(@href,"tel:")]/text()')
                        ],
                    )
                ).strip()
                store_number = "<MISSING>"

                location_type = "<MISSING>"

                # todo
                hours_of_operation = "<MISSING>"

                latitude, longitude = (
                    store_res.text.split("lat:")[1].split(",")[0].strip(),
                    store_res.text.split("lng:")[1].split("},")[0].strip(),
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
                    raw_address=raw_address,
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
