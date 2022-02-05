# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_8
import lxml.html
from sgzip.static import static_zipcode_list
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "renasantbank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

url_list = []


def fetch_data():

    search_url = "https://www.renasantbank.com/api/location/locationfinder/locationsearch?key={}&latitude={}&longitude={}&radius=100"

    zips = static_zipcode_list(radius=200, country_code=SearchableCountries.USA)

    with SgRequests() as session:
        for zip_code in zips:
            log.info(zip_code)
            search = DynamicGeoSearch(
                country_codes=[SearchableCountries.USA],
                expected_search_radius_miles=100,
                max_search_results=50,
                use_state=False,
                granularity=Grain_8(),
            )
            for lat, lng in search:
                log.info(f"pulling records for coordinates: {lat,lng}")
                stores_req = session.get(
                    search_url.format(zip_code, lat, lng), headers=headers
                )
                if isinstance(stores_req, SgRequestError):
                    continue
                stores = json.loads(stores_req.text)["LocationItemList"]
                if stores is not None:
                    for store in stores:
                        if store["Url"] in url_list:
                            continue

                        url_list.append(store["Url"])

                        page_url = "https://www.renasantbank.com" + store["Url"]
                        locator_domain = website
                        location_name = store["LocationName"]

                        log.info(page_url)
                        store_req = session.get(page_url, headers=headers)
                        if store_req.status_code != 200:
                            continue
                        store_sel = lxml.html.fromstring(store_req.text)
                        address = (
                            "".join(
                                store_sel.xpath('//h2[@class="city-address"]//text()')
                            )
                            .strip()
                            .replace("\n", "")
                            .strip()
                        )
                        if len(address) <= 0:
                            continue
                        add_list = address.split(",")
                        street_address = ", ".join(add_list[:-3]).strip()

                        city = add_list[-3].strip()
                        state = add_list[-2].strip()
                        zip = add_list[-1].strip()
                        country_code = "US"

                        store_number = "<MISSING>"
                        phone = store["Phone"]

                        location_type = ", ".join(
                            store_sel.xpath('//div[@class="info-types"]//li/text()')
                        ).strip()
                        sections = store_sel.xpath('//div[@class="info-block"]')
                        hours_of_operation = "<MISSING>"
                        for sec in sections:
                            if (
                                "far fa-clock"
                                == "".join(
                                    sec.xpath('div[@class="info-icon"]/*/@class')
                                ).strip()
                            ):
                                hours_of_operation = (
                                    "; ".join(
                                        sec.xpath('div[@class="info-info"]/p/text()')
                                    )
                                    .strip()
                                    .replace("\n", "")
                                    .strip()
                                )
                                break

                        latitude = store["Latitude"]
                        longitude = store["Longitude"]

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
