# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dodge.com.co"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.dodge.com.co/Concesionarios/"
    api_url = "https://www.dodge.com.co/_dcn/Concesionarios/index.asp?marca=DG"

    with SgRequests() as session:
        search_res = session.get(api_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//div[@class="concesionario"]')

        for no, store in enumerate(stores, 1):

            locator_domain = website

            location_name = "".join(
                store.xpath('.//div[@class="nombre"]//text()')
            ).strip()

            types = store.xpath('.//div[@class="direccion"]')

            for idx, _type in enumerate(types, 1):

                store_info = list(
                    filter(str, [x.strip() for x in _type.xpath(".//text()")])
                )

                if not store_info:
                    continue
                location_type = store_info[0].strip().strip(": ").strip()

                raw_address = (
                    " ".join(store_info[1:])
                    .strip()
                    .split("Tel:")[0]
                    .split("Cel:")[0]
                    .split("Teléfono:")[0]
                    .split("Teléfono(s):")[0]
                    .split("Nit:")[0]
                    .strip()
                )

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = formatted_addr.city
                if not city:
                    city = "".join(
                        store.xpath('./div[@class="ciudad"]//text()')
                    ).strip()
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "CO"
                phone = " ".join(store_info[1:]).strip()

                if "Tel:" in phone:
                    phone = phone.split("Tel:")[1].split("Cel:")[0].strip()
                elif "Teléfono" in phone:
                    phone = phone.split("ono")[1].split(":")[1].strip()
                elif "Nit:" in phone:
                    phone = phone.split("Nit:")[1].strip()
                else:
                    phone = "<MISSING>"

                if "Posventa" in phone:
                    location_type = "Posventa"

                page_url = search_url

                hours_of_operation = "<MISSING>"

                store_number = "<MISSING>"

                latitude, longitude = "<MISSING>", "<MISSING>"

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
                    phone=phone.replace("Celular", "")
                    .strip()
                    .replace("Posventa", "")
                    .strip()
                    .split(" y")[0]
                    .strip()
                    .split(" - ")[0]
                    .strip(),
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
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
