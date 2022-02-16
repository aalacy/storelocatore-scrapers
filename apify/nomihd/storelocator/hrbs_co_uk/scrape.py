# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "hrbs.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.hrbs.co.uk",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    urls_list = [
        "https://www.hrbs.co.uk/branches/",
        "https://www.hrbs.co.uk/branches/agencies/",
    ]
    with SgRequests() as session:
        for search_url in urls_list:
            if "/branches/agencies" in search_url:
                location_type = "agency"
                params = (
                    ("action", "mapp_query"),
                    ("list", "1"),
                    ("name", "mapp0"),
                    ("query[meta_key]", "branch"),
                    ("query[meta_value]", "no"),
                    ("query[posts_per_page]", "-1"),
                    ("query[post_type]", "page"),
                    ("query[order]", "ASC"),
                    ("debug", ""),
                )
            else:
                location_type = "branch"
                params = (
                    ("action", "mapp_query"),
                    ("list", "1"),
                    ("name", "mapp0"),
                    ("query[meta_key]", "branch"),
                    ("query[meta_value]", "yes"),
                    ("query[posts_per_page]", "-1"),
                    ("query[post_type]", "page"),
                    ("query[order]", "DESC"),
                    ("debug", ""),
                )
            stores_req = session.get(
                "https://www.hrbs.co.uk/wp-admin/admin-ajax.php",
                headers=headers,
                params=params,
            )
            stores = json.loads(stores_req.text)["data"]["pois"]
            for store in stores:
                page_url = store["url"]
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                locator_domain = website
                location_name = store["title"]
                if "Head Office" == location_name:
                    continue
                raw_address = (
                    store["body"]
                    .replace("<p>", "")
                    .replace("</p>", "")
                    .strip()
                    .replace("\n", "")
                    .strip()
                    .split(",")
                )

                street_address = (
                    ", ".join(raw_address[:-3])
                    .strip()
                    .replace("Robert Taylor,", "")
                    .strip()
                )
                city = raw_address[-3]

                state = "".join(raw_address[-2]).strip()
                zip = "".join(raw_address[-1]).strip()
                country_code = "GB"
                phone = (
                    "".join(
                        store_sel.xpath(
                            '//section[@class="entry"]/p[contains(text(),"Telephone")]//text()'
                        )
                    )
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                    .replace("Telephone:", "")
                    .strip()
                )

                store_number = "<MISSING>"
                hours_of_operation = (
                    "; ".join(store_sel.xpath('//section[@class="entry"]/h4/text()'))
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                    .replace("day", "day:")
                    .strip()
                )

                latitude = store["point"]["lat"]
                longitude = store["point"]["lng"]
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
