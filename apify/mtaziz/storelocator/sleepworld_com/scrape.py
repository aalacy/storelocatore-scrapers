from sgrequests import SgRequests
from lxml import html
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("sleepworld_com")
DOMAIN = "sleepworld.com"
MISSING = SgRecord.MISSING


def fetch_data():
    with SgRequests() as session:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
        }

        api_endpoint_url = "https://www.sleepworld.com/amlocator/index/ajax/"
        json_data = session.get(api_endpoint_url, headers=headers).json()

        # Corporate address deleted
        del json_data["items"][33]
        sel2 = html.fromstring(json_data["block"], "lxml")
        purls = sel2.xpath('//a[contains(text(), " Store Details")]/@href')
        purls = ["https://www.sleepworld.com" + pu for pu in purls]
        location_names = sel2.xpath('//div[@class="amlocator-title"]/text()')

        for idx, d in enumerate(json_data["items"][0:]):
            locator_domain = DOMAIN
            popup_html = d["popup_html"]
            sel = html.fromstring(popup_html, "lxml")
            page_url = purls[idx]
            page_url = page_url if page_url else MISSING
            logger.info(f"[{idx}] Page URL: {page_url}")

            location_name = location_names[idx]
            if location_name:
                location_name = " ".join(location_name.split())
            else:
                location_name = MISSING

            logger.info(f"[{idx}] Location Name: {location_name}")

            address_raw = sel.xpath("//div[@class='map-add-text']/text()")
            address_raw1 = "".join(address_raw)
            address_raw2 = " ".join(address_raw1.split())
            address_raw2 = address_raw2.replace(" ,", ",")
            pai = parse_address_intl(address_raw2)

            city = pai.city
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            zip_postal = pai.postcode
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[{idx}] zip_postal: {zip_postal}")

            street_address = pai.street_address_1
            street_address = street_address if street_address else MISSING
            logger.info(f"[{idx}] street_address: {street_address}")

            state = pai.state
            state = state if state else MISSING
            logger.info(f"[{idx}] state: {state}")

            country_code = "US"
            store_number = d["id"]
            logger.info(f"[{idx}] store_number: {store_number}")

            phone_data = sel.xpath("//div[@class='contact-us-text']/text()")
            phone_data = "".join(phone_data)
            phone_data = phone_data.strip()
            phone = phone_data if phone_data else MISSING
            logger.info(f"[{idx}] phone_number: {phone}")

            location_type = "Mattress Store"
            latitude = d["lat"]
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] latitude: {latitude}")

            longitude = d["lng"]
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] longitude: {longitude}")
            hours_of_operation = ""
            store_time = sel.xpath('//div[@class="map-store-time"]//text()')
            store_time1 = [" ".join(st.split()) for st in store_time]
            store_time1 = [st for st in store_time1 if st]
            if store_time1:
                hours_of_operation = ", ".join(store_time1)
            else:
                hours_of_operation = MISSING
            raw_address = address_raw2 or MISSING

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
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
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
