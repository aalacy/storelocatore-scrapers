# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from bs4 import BeautifulSoup as BS

website = "communitymedicalgroup.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.communitymedicalgroup.com/content/about/locations.php"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    sections = search_sel.xpath('//div[@class="container-about"]/div/a/@href')
    for sec_url in sections:
        stores_req = session.get(
            "https://www.communitymedicalgroup.com" + sec_url, headers=headers
        )
        stores_sel = lxml.html.fromstring(stores_req.text)

        json_text = (
            "["
            + stores_req.text.split("all = [")[1]
            .strip()
            .split("];")[0]
            .strip()
            .rsplit("],", 1)[0]
            .strip()
            + "]]"
        )

        json_text = json_text.replace("'", '"')
        stores_json = json.loads(json_text)

        for store in stores_json:
            page_url = (
                "https://www.communitymedicalgroup.com"
                + "".join(
                    stores_sel.xpath(
                        f'//div[@id="ab{store[7]}"]//a[contains(text(),"VIEW LOCATION")]/@href'
                    )
                ).strip()
            )
            locator_domain = website

            location_name = store[0].strip()

            street_address = store[1].strip()

            city = store[2].strip().split(",")[0].strip()
            if city.isdigit():
                city = "<MISSING>"
            state = store[2].strip().split(",")[1].strip().split(" ")[0].strip()
            zip = store[2].strip().split(",")[1].strip().split(" ")[-1].strip()

            country_code = "US"

            store_number = page_url.split("?l=")[1].strip()

            phone = store[5].strip()
            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            log.info(page_url)
            store_req = session.get(page_url)
            soup = BS(store_req.text, "lxml")

            try:
                raw_info = list(
                    soup.find_all("div", {"id": "locationsinfo"})[0].stripped_strings
                )
                for index in range(0, len(raw_info)):
                    if "Hours of Operation" in raw_info[index]:
                        hours_of_operation = " ".join(raw_info[index + 1 :]).strip()
                        try:
                            hours_of_operation = (
                                hours_of_operation.split("Laboratory")[0]
                                .strip()
                                .replace("day", "day:")
                                .replace("pm ", "pm; ")
                                .strip()
                            )
                        except:
                            pass

            except:
                pass
            latitude = store[3]
            longitude = store[4]

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
