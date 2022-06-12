import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests import SgRequests, SgRequestError
from sgpostal import sgpostal as parser

logger = SgLogSetup().get_logger("circlek.com")


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.circlek.com"

    found_poi = []
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    location_urls = [
        "https://www.circlek.com/stores_new.php?lat=33.6&lng=-112.12&distance=10000000&services=gas,diesel&region=global&page={}"
    ]

    with SgRequests(dont_retry_status_codes=([404])) as session:
        for location_url in location_urls:
            page_no = 0
            while True:
                stores = session.get(
                    location_url.format(page_no), headers=headers
                ).json()["stores"]
                if len(stores) <= 0:
                    break
                logger.info("Processing %s links.." % (len(stores)))
                for key in stores.keys():
                    if stores[key]["country"].upper() != "GUAM":
                        if (
                            stores[key]["display_brand"] == "Circle K"
                            and stores[key]["op_status"] != "Planned"
                            and stores[key]["op_status"] != "Future"
                        ):
                            page_url = "https://www.circlek.com" + stores[key]["url"]
                            logger.info(page_url)
                            if page_url in found_poi:
                                continue
                            found_poi.append(page_url)
                            store_req = session.get(page_url, headers=headers)
                            if isinstance(store_req, SgRequestError):
                                continue
                            store_sel = lxml.html.fromstring(store_req.text)
                            json_list = store_sel.xpath(
                                '//script[@type="application/ld+json"]/text()'
                            )
                            for js in json_list:
                                if "ConvenienceStore" in js:
                                    try:
                                        store_json = json.loads(js, strict=False)
                                    except:
                                        continue
                                    location_name = (
                                        store_json["name"].replace("&amp;", "&").strip()
                                    )
                                    if stores[key]["franchise"] == "1":
                                        location_type = "Brand Store"
                                    else:
                                        location_type = (
                                            "Dealer/Distributor/Retail Partner"
                                        )

                                    phone = store_json["telephone"]
                                    street_address = (
                                        store_json["address"]["streetAddress"]
                                        .replace("  ", " ")
                                        .replace("r&#039;", "'")
                                        .replace("&amp;", "&")
                                        .strip()
                                    )
                                    if street_address[-1:] == ",":
                                        street_address = street_address[:-1]
                                    city = (
                                        stores[key]["city"]
                                        .replace("&#039;", "'")
                                        .strip()
                                    )
                                    zipp = store_json["address"]["postalCode"].strip()
                                    country_code = stores[key]["country"]
                                    latitude = store_json["geo"]["latitude"]
                                    longitude = store_json["geo"]["longitude"]
                                    store_number = stores[key]["cost_center"]
                                    state = ""
                                    try:
                                        temp_address = "".join(
                                            store_sel.xpath(
                                                '//h2[@class="heading-small"]//text()'
                                            )
                                        ).strip()
                                        formatted_addr = parser.parse_address_intl(
                                            temp_address
                                        )

                                        state = formatted_addr.state

                                    except:
                                        state = "<MISSING>"

                                    hours = store_sel.xpath(
                                        '//div[@class="columns large-12 middle hours-wrapper"]/div[contains(@class,"hours-item")]'
                                    )
                                    hours_list = []
                                    for hour in hours:
                                        day = "".join(
                                            hour.xpath("span[1]/text()")
                                        ).strip()
                                        time = "".join(
                                            hour.xpath("span[2]/text()")
                                        ).strip()
                                        hours_list.append(day + ":" + time)

                                    hours_of_operation = "; ".join(hours_list).strip()
                                    if (
                                        stores[key]["op_status"]
                                        == "Limitation COVID-19"
                                    ):
                                        hours_of_operation = (
                                            "Coming Soon/Limitation COVID-19"
                                        )

                                    if street_address == "" or street_address is None:
                                        street_address = stores[key]["address"]
                                    if not street_address:
                                        street_address = "<MISSING>"

                                    if hours_of_operation == "":
                                        try:
                                            hours_of_operation = " ".join(
                                                store_sel.xpath(
                                                    '//div[@class="columns large-12 middle hours-wrapper"]/text()'
                                                )
                                            ).strip()
                                        except:
                                            hours_of_operation = "<MISSING>"

                                    if not hours_of_operation:
                                        hours_of_operation = "<MISSING>"

                                    if "-" not in phone:
                                        phone = "<MISSING>"

                                    yield SgRecord(
                                        locator_domain=locator_domain,
                                        page_url=page_url,
                                        location_name=location_name,
                                        street_address=street_address,
                                        city=city,
                                        state=state,
                                        zip_postal=zipp,
                                        country_code=country_code,
                                        store_number=store_number,
                                        phone=phone,
                                        location_type=location_type,
                                        latitude=latitude,
                                        longitude=longitude,
                                        hours_of_operation=hours_of_operation,
                                    )
                page_no = page_no + 1


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
