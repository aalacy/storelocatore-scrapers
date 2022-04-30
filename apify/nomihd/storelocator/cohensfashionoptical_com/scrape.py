# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

website = "www.cohensfashionoptical.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.cohensfashionoptical.com",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.cohensfashionoptical.com/store-finder/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    api_url = "https://www.cohensfashionoptical.com/findermap/views/all_stores.php?criteria={%22ajaxurl%22:%22%22,%22lat%22:%22%22,%22lng%22:%22%22,%22current_lat%22:%22%22,%22current_lng%22:%22%22,%22category_id%22:%22%22,%22max_distance%22:%22%22,%22page_number%22:PAGENO,%22nb_display%22:10,%22map_all_stores%22:%220%22,%22marker_icon%22:%22%22,%22marker_icon_current%22:%22https://www.cohensfashionoptical.com/findermap/marker-current.png%22,%22autodetect_location%22:%221%22,%22streetview_display%22:1,%22search_str%22:%22STATE%22,%22display_type%22:%22%22,%22current_latitude%22:%22%22,%22current_longitude%22:%22%22}"

    with SgRequests() as session:
        us_states = us.states.STATES
        states_list = []
        for st in us_states:
            states_list.append(st.abbr)

        states_list.append("PR")
        states_list.append("New York")

        for st in states_list:
            log.info(f"fetching data for state: {st}")
            for pn in range(1, 100):

                final_url = api_url.replace("PAGENO", str(pn)).replace("STATE", st)
                api_res = session.get(
                    final_url,
                    headers=headers,
                )
                json_res = json.loads(api_res.text)

                stores = json_res["locations"]
                if not stores:
                    break

                for store in stores:

                    locator_domain = website

                    location_name = store["title"].strip()
                    page_url = store["store_link"].strip()

                    location_type = "<MISSING>"
                    log.info(page_url)
                    store_res = session.get(page_url, headers=headers)
                    store_sel = lxml.html.fromstring(store_res.text)
                    location_type = "".join(
                        store_sel.xpath('//span[@class="locationClosed"]/text()')
                    ).strip()
                    if location_type:
                        location_type = "Temporarily " + location_type

                    phone = store["address_phone"]

                    hours = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    '//div[@id="storeHours"]//text()'
                                )
                            ],
                        )
                    )
                    if hours:
                        hours_of_operation = (
                            "; ".join(hours[1:])
                            .replace("Wed;", "Wed:")
                            .replace("Thurs;", "Thurs:")
                            .replace("Fri;", "Fri:")
                            .replace("Sat;", "Sat:")
                            .replace("Sun;", "Sun:")
                            .replace("Tue;", "Tue:")
                            .replace("Mon;", "Mon:")
                        )
                    else:
                        hours_of_operation = "<MISSING>"

                    raw_address = "<MISSING>"

                    street_address = store["store_address"]
                    if not street_address or len(street_address) <= 0:
                        street_address = "".join(
                            store_sel.xpath("//address/span[1]/text()")
                        ).strip()

                    city = store["address_city"]
                    state = store["address_state"]
                    zip = store["address_zipcode"]

                    country_code = "US"

                    store_number = store["id"]

                    latitude, longitude = store["latitude"], store["longitude"]

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
