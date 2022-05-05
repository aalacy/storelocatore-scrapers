# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "annuaire-mairie.fr/centre-commercial.html"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Referer": "https://www.annuaire-mairie.fr/centre-commercial-departement-drome.html",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.annuaire-mairie.fr/centre-commercial.html"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)
        regions_sel = lxml.html.fromstring(search_res.text)
        regions = regions_sel.xpath('//ul[@class="annonce annonce_unesco"]/li[div]')
        for region in regions:
            region_url = "".join(
                region.xpath('.//div[contains(@class,"annonce_titre")]/a/@href')
            ).strip()
            if (
                "Plus"
                in "".join(
                    region.xpath('.//div[@class="annonce_bouton"]/text()')
                ).strip()
            ):
                log.error("\n\ngetting straight to details page\n\n")
                state = "<MISSING>"
                locator_domain = website
                page_url = "https://www.annuaire-mairie.fr" + region_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                if isinstance(store_req, SgRequestError):
                    continue

                location_name = "".join(
                    store_sel.xpath('//div[@id="content"]/h1/text()')
                ).strip()
                location_type = "<MISSING>"

                raw_address = (
                    ", ".join(
                        store_sel.xpath(
                            '//div[@class="ville_info"]/p[./span[@class="fa fa-envelope"]]/text()'
                        )
                    )
                    .strip()
                    .replace("\n", "")
                    .strip()
                )

                if len(raw_address) > 0 and raw_address[0] == ",":
                    raw_address = "".join(raw_address[1:]).strip()

                street_address = ", ".join(raw_address.split(",")[:-1]).strip()
                city = raw_address.split(",")[-1].strip().split(" ", 1)[-1].strip()
                zip = raw_address.split(",")[-1].strip().split(" ", 1)[0].strip()
                country_code = "FR"

                phone = (
                    "".join(
                        store_sel.xpath(
                            '//div[@class="ville_info"]//a[contains(@href,"tel:")]/@href'
                        )
                    )
                    .strip()
                    .replace("tel:", "")
                    .strip()
                )
                hours_of_operation = "; ".join(
                    store_sel.xpath(
                        '//div[@class="ville_info"]/p[./span[@class="fa fa-clock"]]/text()'
                    )
                ).strip()
                if len(hours_of_operation) > 0 and hours_of_operation[0] == ";":
                    hours_of_operation = "".join(hours_of_operation[1:]).strip()
                store_number = "<MISSING>"
                latitude = "<MISSING>"
                try:
                    latitude = (
                        store_req.text.split("L.LatLng(")[1]
                        .strip()
                        .split(",")[0]
                        .strip()
                    )
                except:
                    pass

                longitude = "<MISSING>"
                try:
                    longitude = (
                        store_req.text.split("L.LatLng(")[1]
                        .strip()
                        .split(",")[1]
                        .strip()
                        .split(")")[0]
                        .strip()
                    )
                except:
                    pass

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
            else:
                district_req = session.get(
                    "https://www.annuaire-mairie.fr" + region_url, headers=headers
                )
                district_sel = lxml.html.fromstring(district_req.text)
                district_titles = district_sel.xpath(
                    '//div[@id="content"]/h3[contains(@id,"arr_")]'
                )
                district_sections = district_sel.xpath(
                    '//div[@id="content"]/div[contains(@id,"_content")]'
                )
                for index in range(0, len(district_titles)):
                    state = (
                        "".join(district_titles[index].xpath("text()"))
                        .strip()
                        .replace("Arrondissement", "")
                        .strip()
                    )
                    stores = district_sections[index].xpath(".//a/@href")
                    for store_url in stores:
                        locator_domain = website
                        page_url = "https://www.annuaire-mairie.fr" + store_url
                        log.info(page_url)
                        store_req = session.get(page_url, headers=headers)
                        store_sel = lxml.html.fromstring(store_req.text)

                        if isinstance(store_req, SgRequestError):
                            continue

                        location_name = "".join(
                            store_sel.xpath('//div[@id="content"]/h1/text()')
                        ).strip()
                        location_type = "<MISSING>"

                        raw_address = (
                            ", ".join(
                                store_sel.xpath(
                                    '//div[@class="ville_info"]/p[./span[@class="fa fa-envelope"]]/text()'
                                )
                            )
                            .strip()
                            .replace("\n", "")
                            .strip()
                        )
                        if len(raw_address) > 0 and raw_address[0] == ",":
                            raw_address = "".join(raw_address[1:]).strip()

                        street_address = ", ".join(raw_address.split(",")[:-1]).strip()
                        city = (
                            raw_address.split(",")[-1].strip().split(" ", 1)[-1].strip()
                        )
                        zip = (
                            raw_address.split(",")[-1].strip().split(" ", 1)[0].strip()
                        )
                        country_code = "FR"

                        phone = (
                            "".join(
                                store_sel.xpath(
                                    '//div[@class="ville_info"]//a[contains(@href,"tel:")]/@href'
                                )
                            )
                            .strip()
                            .replace("tel:", "")
                            .strip()
                        )
                        hours_of_operation = "; ".join(
                            store_sel.xpath(
                                '//div[@class="ville_info"]/p[./span[@class="fa fa-clock"]]/text()'
                            )
                        ).strip()
                        if len(hours_of_operation) > 0 and hours_of_operation[0] == ";":
                            hours_of_operation = "".join(hours_of_operation[1:]).strip()
                        store_number = "<MISSING>"
                        latitude = "<MISSING>"
                        try:
                            latitude = (
                                store_req.text.split("L.LatLng(")[1]
                                .strip()
                                .split(",")[0]
                                .strip()
                            )
                        except:
                            pass

                        longitude = "<MISSING>"
                        try:
                            longitude = (
                                store_req.text.split("L.LatLng(")[1]
                                .strip()
                                .split(",")[1]
                                .strip()
                                .split(")")[0]
                                .strip()
                            )
                        except:
                            pass

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
