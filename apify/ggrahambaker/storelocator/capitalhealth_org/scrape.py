from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

log = sglog.SgLogSetup().get_logger(logger_name="capitalhealth.org")
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locator_domain = "https://www.capitalhealth.org"
    search_url = "https://www.capitalhealth.org/our-locations/result?field_services_target_id=All&field_search_city_target_id=All&field_location_type_target_id=All&field_location_name_value=&page=0"
    while True:

        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//h2[@class="v-listing__title"]/a/@href')
        for store_url in stores:
            page_url = locator_domain + store_url
            log.info(page_url)

            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_name = "".join(store_sel.xpath("//h1//text()")).strip()
            street_address = "".join(
                store_sel.xpath(
                    '//p[@class="address"]/span[@class="address-line1"]/text()'
                )
            ).strip()
            city = "".join(
                store_sel.xpath('//p[@class="address"]/span[@class="locality"]/text()')
            ).strip()
            state = "".join(
                store_sel.xpath(
                    '//p[@class="address"]/span[@class="administrative-area"]/text()'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//p[@class="address"]/span[@class="postal-code"]/text()'
                )
            ).strip()
            country_code = "".join(
                store_sel.xpath('//p[@class="address"]/span[@class="country"]/text()')
            ).strip()
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="field field--name-field-phone field--type-telephone field--label-inline f-phone"]//a/text()'
                )
            ).strip()
            location_type = "<MISSING>"
            store_number = "<MISSING>"
            hours_of_operation = ""
            hours = store_sel.xpath(
                '//div[@class="clearfix text-formatted field field--name-field-office-hours field--type-text-long field--label-hidden f-office-hours field__item"]/p'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("strong/text()")).strip()
                time = "".join(hour.xpath("text()")).strip()
                if len(day) > 0 and len(time) > 0 and time != ".":
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = ""
            longitude = ""
            map_link = "".join(
                store_sel.xpath('//a[contains(@href,"/maps/dir")]/@href')
            ).strip()
            if len(map_link) > 0:
                if "/@" in map_link:
                    latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                    longitude = map_link.split("/@")[1].strip().split(",")[1]

            yield SgRecord(
                locator_domain="https://interstatebatteries.com",
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

        next_page = stores_sel.xpath('//a[@rel="next"]/@href')
        if len(next_page) > 0:
            search_url = (
                "https://www.capitalhealth.org/our-locations/result" + next_page[0]
            )
            log.info(f"processing next page having url: {search_url}")
        else:
            break


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
