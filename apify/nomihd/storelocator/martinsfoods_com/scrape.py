from sgrequests import SgRequests, SgRequestError
import json
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "martinsfoods.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(proxy_country="us", dont_retry_status_codes=([404]))
headers = {
    "authority": "martinsfoods.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://martinsfoods.com/store-locator",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_hours_of_operation(hours_of_operation_list):

    hours_of_operation = ""
    for hour in hours_of_operation_list:
        hours_of_operation = (
            hours_of_operation
            + "".join(
                hour.xpath('td[@class="c-location-hours-details-row-day"]' "/text()")
            ).strip()
            + " "
            + "".join(
                hour.xpath(
                    'td[@class="c-location-hours-details-row-intervals"]'
                    '//span[@class="c-location-hours-details-row-intervals-instance-open"]'
                    "/text()"
                )
            ).strip()
            + "-"
            + "".join(
                hour.xpath(
                    'td[@class="c-location-hours-details-row-intervals"]'
                    '//span[@class="c-location-hours-details-row-intervals-instance-close"]'
                    "/text()"
                )
            ).strip()
            + " "
        )

    return hours_of_operation


def set_gas_station_variables(store_sel, page_url, location_name, store_number):
    locator_domain = website
    page_url = page_url
    location_name = location_name
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = store_number
    phone = ""
    location_type = "GAS_STATION"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    street_address = "".join(
        store_sel.xpath(
            '//div[@class="GasStation-address"]'
            '//span[@class="c-address-street-1"]/text()'
        )
    ).strip()
    city = "".join(
        store_sel.xpath(
            '//div[@class="GasStation-address"]'
            '//span[@class="c-address-city"]/text()'
        )
    ).strip()
    state = "".join(
        store_sel.xpath(
            '//div[@class="GasStation-address"]'
            '//span[@class="c-address-state"]/text()'
        )
    ).strip()
    zip = "".join(
        store_sel.xpath(
            '//div[@class="GasStation-address"]'
            '//span[@class="c-address-postal-code"]/text()'
        )
    ).strip()

    latitude = "".join(
        store_sel.xpath('//div[@class="GasStation-distance"]' "/span/@data-latitude")
    ).strip()
    longitude = "".join(
        store_sel.xpath('//div[@class="GasStation-distance"]' "/span/@data-longitude")
    ).strip()

    country_code = "".join(
        store_sel.xpath(
            '//div[@class="GasStation-address"]//abbr[@itemprop="addressCountry"]/text()'
        )
    ).strip()
    if country_code == "":
        country_code = "<MISSING>"

    phone = "".join(
        store_sel.xpath(
            '//span[@class="c-phone-number-span c-phone-gas-station-phone-number-span"]/text()'
        )
    ).strip()
    if phone == "":
        phone = "<MISSING>"

    hours_of_operation_list = store_sel.xpath(
        '//div[@id="gas-collapse-hours"]' "//table/tbody/tr"
    )

    hours_of_operation = get_hours_of_operation(hours_of_operation_list)
    hours_of_operation = hours_of_operation.strip()
    if hours_of_operation == "":
        hours_of_operation = "<MISSING>"

    return SgRecord(
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


def fetch_data():
    # Your scraper here
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    store_types = ["GROCERY", "GAS_STATION"]
    for s in store_types:
        locations_resp = session.get(
            "https://martinsfoods.com/apis/store-locator/locator/v1/stores/MRTN?storeType="
            + s.strip()
            + "&maxDistance=10000&details=true",
            headers=headers,
        )

        locations = json.loads(locations_resp.text)["stores"]

        for l in locations:
            location_name = l["name"]
            street_address = l["address1"]
            if len(l["address2"]) > 0:
                street_address = street_address + "\n" + l["address2"]

            city = l["city"]
            state = l["state"]
            zip = l["zip"]
            store_number = l["storeNo"]
            location_type = l["storeType"]
            if location_type == "":
                location_type = "<MISSING>"
            latitude = l["latitude"]
            longitude = l["longitude"]

            store_url = "https://stores.martinsfoods.com/" + store_number
            log.info(store_url)
            store_resp = session.get(store_url, headers=headers)
            if isinstance(store_resp, SgRequestError):
                log.error(store_url)
                continue
            store_sel = lxml.html.fromstring(store_resp.text)
            country_code = "".join(
                store_sel.xpath(
                    '//span[@itemprop="address"]//abbr[@itemprop="addressCountry"]/text()'
                )
            ).strip()
            if country_code == "":
                country_code = "<MISSING>"

            phone = "".join(
                store_sel.xpath(
                    '//div[@class="NAP-info l-container"]//span[@itemprop="telephone"]/text()'
                )
            ).strip()
            if phone == "":
                phone = "<MISSING>"
            page_url = store_url
            hours_of_operation_list = store_sel.xpath(
                '//div[@class="StoreDetails-hours--desktop u-hidden-xs"]'
                "//table/tbody/tr"
            )

            hours_of_operation = get_hours_of_operation(hours_of_operation_list)

            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"

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
            GasStation = store_sel.xpath('//div[@class="GasStation"]')
            if len(GasStation) > 0:
                curr_sgrecord = set_gas_station_variables(
                    store_sel, page_url, location_name, store_number
                )
                yield curr_sgrecord
            # break


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
