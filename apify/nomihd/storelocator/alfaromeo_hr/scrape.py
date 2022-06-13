# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "alfaromeo.hr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.alfaromeo.hr",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.fiat.hr",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_urls = [
        "https://www.alfaromeo.hr/prodajno-servisna-mreza/",
        "https://www.alfaromeo.si/prodajno-servisna-mreza/",
    ]
    api_urls = [
        "https://avtotriglav.specto.si/hr/alfa-romeo-prodajno-servisna-mreza/",
        "https://avtotriglav.specto.si/prodajno-servisna-mreza-alfa-romeo/",
    ]

    with SgRequests() as session:
        for index in range(0, len(api_urls)):
            api_res = session.get(api_urls[index], headers=headers)

            html_sel = lxml.html.fromstring(api_res.text)
            html_sel = lxml.html.fromstring(api_res.text)
            sections = html_sel.xpath('//div[@class="group-single"]')
            for section in sections:
                location_type = "".join(section.xpath("span/text()")).strip()

                stores = section.xpath('.//input[@type="checkbox"]')

                for store in stores:

                    locator_domain = website

                    location_name = "".join(store.xpath("./@data-title"))
                    page_url = search_urls[index]

                    store_info = "".join(store.xpath("./@data-description"))

                    raw_address = (
                        store_info.split("<br><hr>")[0]
                        .replace("<br>", ", ")
                        .replace("  ", " ")
                        .strip()
                        .replace(",,", ",")
                        .replace(", ,", ",")
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
                    state = formatted_addr.state
                    zip = formatted_addr.postcode

                    country_code = (
                        page_url.split("alfaromeo.")[1].strip().split("/")[0].strip()
                    )

                    phn_hoo = "".join(store_info.split("<br><hr>")[1:])
                    sel = lxml.html.fromstring(phn_hoo)

                    data = " ".join(sel.xpath("//text()"))

                    if "Telefon:" in data:

                        phone = (
                            data.split("Telefon:")[1]
                            .split("E-mail")[0]
                            .strip()
                            .split("E-naslov")[0]
                            .strip()
                        )
                        try:
                            hours_of_operation = (
                                data.split("Kontakt")[0]
                                .split("Radno vrijeme")[1]
                                .strip()
                                .replace("\n", ";")
                                .replace(" ;", ";")
                                .replace(".", "")
                                .replace("\r", "")
                                .strip()
                                .replace(" ;", "; ")
                            )
                        except:
                            hours_of_operation = (
                                data.split("Kontakt")[0]
                                .split("Delovni ")[1]
                                .strip()
                                .replace("\n", ";")
                                .replace(" ;", ";")
                                .replace(".", "")
                                .replace("\r", "")
                                .strip()
                                .replace(" ;", "; ")
                            )
                    else:
                        phone = "<MISSING>"
                        try:
                            hours_of_operation = (
                                data.split("Radno vrijeme")[1]
                                .strip()
                                .replace("\n", ";")
                                .replace(" ;", ";")
                                .replace(".", "")
                                .replace("\r", "")
                                .strip()
                                .replace(" ;", "; ")
                            )
                        except:
                            hours_of_operation = (
                                data.split("Delovni ")[1]
                                .strip()
                                .replace("\n", ";")
                                .replace(" ;", ";")
                                .replace(".", "")
                                .replace("\r", "")
                                .strip()
                                .replace(" ;", "; ")
                            )

                    store_number = "<MISSING>"

                    latitude, longitude = (
                        "".join(store.xpath("./@data-latitude")),
                        "".join(store.xpath("./@data-longitude")),
                    )
                    if "<br />" in latitude:
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
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
