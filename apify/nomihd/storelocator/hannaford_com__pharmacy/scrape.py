# -*- coding: utf-8 -*-
from sgrequests import SgRequests
import json
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "hannaford.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_formated_street_address(street_address):

    if "&nbsp;" in street_address:
        add_before_nbsp = street_address.split("&nbsp;")[0].strip()
        if add_before_nbsp[0].isdigit():
            street_address = (
                street_address.split("&nbsp;")[0].strip().replace(",", "").strip()
            )
        else:
            add_after_nbsp = (
                street_address.split("&nbsp;")[1].strip().replace(",", "").strip()
            )
            if add_after_nbsp[0].isdigit():
                street_address = add_after_nbsp.replace("&nbsp;", " ").strip()
            else:
                street_address = street_address.replace("&nbsp;", " ").strip()

    return street_address


def fetch_data():
    # Your scraper here
    locator_domain = website
    with SgRequests() as session:
        sitemap_resp = session.get(
            "https://www.hannaford.com/sitemap/store_1.xml",
            headers=headers,
        )

        store_links = sitemap_resp.text.split("<loc>")
        for store in store_links:
            if "/locations/" in store:
                store_url = store.split("</loc>")[0].strip()
                log.info(store_url)
                store_resp = session.get(store_url, headers=headers)
                store_sel = lxml.html.fromstring(store_resp.text)
                json_data = json.loads(
                    "".join(
                        store_sel.xpath(
                            '//script[@type="application/ld+json"]' "/text()"
                        )
                    )
                )

                location_name = json_data["name"]
                street_address = json_data["address"]["streetAddress"].strip()
                street_address = get_formated_street_address(street_address)

                city = json_data["address"]["addressLocality"]
                state = json_data["address"]["addressRegion"]
                zip = json_data["address"]["postalCode"]
                store_number = store_url.split("/")[-1].split("-")[-1].strip()
                location_type = store_sel.xpath(
                    '//li[@class="storeContact-info"]/text()'
                )
                if len(location_type) > 0:
                    location_type = location_type[0]
                else:
                    location_type = "<MISSING>"

                if "pharmacy" not in location_type.lower():
                    continue

                latitude = json_data["geo"]["latitude"]
                longitude = json_data["geo"]["longitude"]

                country_code = json_data["address"]["addressCountry"]
                if country_code == "":
                    country_code = "<MISSING>"

                phone = "".join(
                    store_sel.xpath(
                        '//li[@class="storeContact-info small-text"][contains(text(),"Pharmacy")]/a/text()'
                    )
                ).strip()

                page_url = store_url

                hours = store_sel.xpath('//div[@class="hoursDisplay pharmacy"]/p')
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("text()")).strip()
                    time = "".join(hour.xpath("span/text()")).strip()
                    hours_list.append(day + time)

                hours_of_operation = "; ".join(hours_list).strip()

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
