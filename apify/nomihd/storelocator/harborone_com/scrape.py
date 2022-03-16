# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html


website = "harborone.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.harborone.com",
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

    base = "https://www.harborone.com"
    search_url = "https://www.harborone.com/resources/branch-atm-locations"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = list(
        set(search_sel.xpath('//a[contains(@href,"/Branch-ATM-Locations/") ]/@href'))
    )

    for store in stores_list:

        page_url = base + store
        if "No-ATM-Or-Branch" in page_url:
            continue

        log.info(page_url)

        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        json_res = json.loads(
            store_res.text.split('<script type="application/ld+json">')[1]
            .split("</script>")[0]
            .strip()
            .strip("} ")
            .strip()
            .strip(",")
            .strip()
            .replace("\r", "")
            .replace('"\n    "', '",\n    "')
        )

        if json_res["@type"] == "FinancialService":  # Ignore atm
            continue

        locator_domain = website

        location_name = "".join(
            store_sel.xpath('//div[@class="location-detail"]//h1/text()')
        ).strip()

        street_address = (
            json_res["address"]["streetAddress"]
            .strip()
            .replace(", Hospital lower level, across from cafeteria", "")
            .strip()
        )

        city = json_res["address"]["addressLocality"].strip()
        state = json_res["address"]["addressRegion"].strip()

        zip = json_res["address"]["postalCode"].strip()

        country_code = "US"
        store_number = "<MISSING>"

        phone = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[./h2[contains(text(),"HarborOne ")]]/p[1]//text()'
                    )
                ],
            )
        )[-1].strip()

        location_type = "Branch"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[./h2[contains(text(),"Lobby")]]/div//text()'
                    )
                ],
            )
        )
        hours_of_operation = (
            " ".join(hours)
            .replace("PM ", "PM; ")
            .replace("Closed ", "Closed; ")
            .replace("days ", "days: ")
            .strip()
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        raw_address = "<MISSING>"
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
