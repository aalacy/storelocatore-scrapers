# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us
from sgscrape import sgpostal as parser

website = "honeywell.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "sps.honeywell.com",
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


def remove_extra(x):
    if (
        "honeywell.com".upper() in x.upper()
        or "EMAIL" in x.upper()
        or "E-MAIL" in x.upper()
        or "FAX" in x.upper()
        or "SALES" in x.upper()
        or "switchboard".upper() in x.upper()
    ):
        return False
    return True


us_gerneral_num = 0


def fetch_data():
    # Your scraper here
    search_url = "https://sps.honeywell.com/us/en/support/productivity/global-locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    regions = search_sel.xpath('//div[contains(@class,"tab-")]')

    for region in regions:
        page_url = search_url

        locator_domain = website
        store_list = region.xpath('.//div[@class="cmp-text"]')

        for store in store_list:

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//text()")],
                )
            )

            store_info = list(filter(remove_extra, store_info))
            location_name = store_info[0].strip()

            if location_name == "United States & Canada":
                global us_gerneral_num
                us_gerneral_num = (
                    store_info[-1].strip().upper().replace("PHONE:", "").strip()
                )
                continue

            raw_address = (
                " ".join(store_info[1:])
                .split("Tel")[0]
                .split("Phone")[0]
                .split("Technical Support Enquiries")[0]
                .split("Service Center")[0]
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = formatted_addr.country
            country_code = location_name

            phone = (
                store_info[-1]
                .strip()
                .upper()
                .replace("PHONE", "")
                .replace("SUPPORT", "")
                .replace("TECHNICAL", "")
                .replace("TECH", "")
                .replace("TEL", "")
                .strip()
                .strip("():.-# ")
                .strip()
                .split(";")[0]
                .split("(")[0]
                .strip()
            )

            if state and us.states.lookup(state):
                country_code = "US"
                phone = us_gerneral_num

            store_number = "<MISSING>"

            location_type = "<MISSING>"

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
