# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

website = "well.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "finder.well.co.uk",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "origin": "https://finder.well.co.uk",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://finder.well.co.uk/search",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    elif "Location/" in map_link:
        latitude = map_link.split("Location/")[1].split(",")[0].strip()
        longitude = map_link.split("Location/")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    base = "https://finder.well.co.uk"
    search_url = "https://finder.well.co.uk/search"
    url_list = []
    with SgRequests() as session:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.BRITAIN],
            expected_search_radius_miles=15,
            max_search_results=10,
        )
        for lat, lng in search:
            log.info(f"fetching data for coordinates:{lat},{lng}")
            data = {"q": "", "lat": lat, "long": lng}

            search_res = session.post(search_url, headers=headers, data=data)

            search_sel = lxml.html.fromstring(search_res.text)
            stores = search_sel.xpath('//ul[@class="card-list"]/li')

            for no, store in enumerate(stores, 1):

                locator_domain = website

                location_name = "".join(store.xpath(".//h2//text()")).strip()

                location_type = "<MISSING>"

                page_url = base + "".join(
                    store.xpath('.//a[text()="View more info"]//@href')
                )
                if page_url in url_list:
                    continue

                url_list.append(page_url)
                log.info(page_url)
                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                store_info = list(
                    filter(
                        str,
                        [x.strip() for x in store.xpath(".//address//text()")],
                    )
                )
                raw_address = " ".join(store_info)

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")

                city = formatted_addr.city

                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "GB"

                phone = (
                    "".join(store.xpath('.//a[contains(@href,"tel")]//text()'))
                    .replace("Call", "")
                    .strip()
                )

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[h2="Opening hours"]//tr//text()'
                            )
                        ],
                    )
                )
                hours_of_operation = (
                    "; ".join(hours)
                    .replace("day;", "day:")
                    .replace("Fri;", "Fri:")
                    .replace("Sat;", "Sat:")
                    .replace("Sun;", "Sun:")
                    .replace("Thurs;", "Thurs:")
                )

                store_number = "<MISSING>"

                map_link = "".join(store.xpath('.//a[contains(@href,"maps")]/@href'))
                latitude, longitude = get_latlng(map_link)
                search.found_location_at(latitude, longitude)
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
