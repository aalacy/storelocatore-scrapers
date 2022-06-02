# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "casaole.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "casaole.com",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://casaole.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://casaole.com/locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {"action": "loadlocations", "distance": "10000", "group_by": "Market"}


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

    if city and state:
        if not us.states.lookup(state):
            city = city + " " + state
            state = "<MISSING>"

    country_code = "US"
    return street_address, city, state, zip, country_code


def fetch_data():
    # Your scraper here

    api_url = "https://casaole.com/wp-admin/admin-ajax.php"

    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, data=data)

        html_sel = lxml.html.fromstring(api_res.text)
        stores = html_sel.xpath('//div[@class="marker"]')

        for _, store in enumerate(stores, 1):

            locator_domain = website

            location_name = "".join(store.xpath(".//h3/text()"))
            page_url = "".join(store.xpath('.//a[@class="details"]/@href'))

            location_type = "<MISSING>"
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            phone = "".join(store.xpath('.//p[@class="map-phone"]/text()'))

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath('//div[@class="hours"]//text()')
                    ],
                )
            )
            hours_of_operation = "; ".join(hours).replace("day;", "day:").strip()

            raw_address = "<MISSING>"
            full_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath('.//p[@class="nice-address"]//text()')
                    ],
                )
            )

            street_address, city, state, zip, country_code = split_fulladdress(
                full_address
            )

            store_number = "<MISSING>"

            latitude, longitude = "".join(store.xpath("./@data-lat")), "".join(
                store.xpath("./@data-lng")
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
