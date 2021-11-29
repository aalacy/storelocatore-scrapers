# -*- coding: utf-8 -*-
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "premierinn.com"
domain = "https://www.premierinn.com/gb/en/"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.premierinn.com/gb/en/hotels.html"
    with SgRequests(dont_retry_status_codes=([404]), proxy_country="gb") as session:
        towns_req = session.get(search_url, headers=headers)
        towns_sel = lxml.html.fromstring(towns_req.text)
        towns = towns_sel.xpath(
            '//h4[@class="font-size--base pi-hotel-directory__town block"]/a'
        )

        for town in towns:
            town_url = "".join(town.xpath("@href")).strip()
            if "https://www.premierinn.com" not in town_url:
                town_url = domain + town_url

            temp_country = town_url.split("hotels/")[1].strip().split("/")[0].strip()
            if "germany" in temp_country or "republic-of-ireland" in temp_country:
                continue

            county = "".join(town.xpath("text()")).strip()
            stores_req = session.get(town_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//article[@class="seo-hotel-card" and @itemtype="http://schema.org/Hotel"]'
            )
            if len(stores) > 0:
                for store in stores:
                    store_url = "".join(store.xpath("a/@href")).strip()
                    if store_url == "https://www.premierinn.com/gb/en/hotels.html":
                        # fetch from this page
                        page_url = "<MISSING>"
                        locator_domain = website
                        location_name = "".join(
                            store.xpath('.//h3[@class="seo-hotel-card-title"]/text()')
                        ).strip()

                        address = "".join(
                            store.xpath('.//address[@itemprop="address"]/text()')
                        ).strip()

                        street_address = address.split("\n")[0].strip()

                        city = county.replace("Hotels", "").strip()
                        state = "<MISSING>"
                        zip = address.split("\n")[1].strip()

                        country_code = "GB"

                        store_number = "<MISSING>"

                        phone = "<MISSING>"
                        location_type = "<MISSING>"
                        hours_of_operation = "<MISSING>"

                        latitude = "<MISSING>"
                        longitude = "<MISSING>"

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

                    else:
                        if "https://www.premierinn.com" not in store_url:
                            page_url = domain + store_url
                        else:
                            page_url = store_url

                        log.info(page_url)
                        locator_domain = website

                        store_req = session.get(page_url, headers=headers)
                        store_sel = lxml.html.fromstring(store_req.text)

                        sub_stores = store_sel.xpath(
                            '//article[@class="seo-hotel-card"]/a/@href'
                        )

                        if len(sub_stores) > 0:
                            continue

                        location_name = "".join(
                            store_sel.xpath(
                                '//h1[@class="hotel-title__heading hotel-details__title"]/text()'
                            )
                        ).strip()

                        street_address = "".join(
                            store_sel.xpath('//span[@itemprop="streetAddress"]/text()')
                        ).strip()
                        add_2 = "".join(
                            store_sel.xpath(
                                '//span[@itemprop="addressLocality"][1]/text()'
                            )
                        ).strip()
                        if len(add_2) > 0 and not (
                            add_2.replace(" ", "").strip().isalpha()
                        ):
                            street_address = street_address + ", " + add_2

                        city = county.replace("Hotels", "").strip()
                        state = "<MISSING>"
                        zip = "".join(
                            store_sel.xpath('//span[@itemprop="postalCode"]/text()')
                        ).strip()

                        country_code = "GB"

                        store_number = "".join(
                            store_sel.xpath('//meta[@itemprop="hotelCode"]/@content')
                        ).strip()

                        phone = "".join(
                            store_sel.xpath(
                                "//contact-module-responsive/@hotel-phone-number"
                            )
                        ).strip()
                        location_type = "<MISSING>"
                        hours_of_operation = "<MISSING>"

                        latitude = "".join(
                            store_sel.xpath(
                                '//div[@itemprop="geo"]/meta[@itemprop="latitude"]/@content'
                            )
                        ).strip()
                        longitude = "".join(
                            store_sel.xpath(
                                '//div[@itemprop="geo"]/meta[@itemprop="longitude"]/@content'
                            )
                        ).strip()

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

            else:
                page_url = town_url

                log.info(page_url)
                locator_domain = website

                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                sub_stores = store_sel.xpath(
                    '//article[@class="seo-hotel-card"]/a/@href'
                )

                if len(sub_stores) > 0:
                    continue

                location_name = "".join(
                    store_sel.xpath(
                        '//h1[@class="hotel-title__heading hotel-details__title"]/text()'
                    )
                ).strip()

                street_address = "".join(
                    store_sel.xpath('//span[@itemprop="streetAddress"]/text()')
                ).strip()
                add_2 = "".join(
                    store_sel.xpath('//span[@itemprop="addressLocality"][1]/text()')
                ).strip()
                if len(add_2) > 0 and not (add_2.replace(" ", "").strip().isalpha()):
                    street_address = street_address + ", " + add_2

                city = county.replace("Hotels", "").strip()
                state = "<MISSING>"
                zip = "".join(
                    store_sel.xpath('//span[@itemprop="postalCode"]/text()')
                ).strip()

                country_code = "GB"

                store_number = "".join(
                    store_sel.xpath('//meta[@itemprop="hotelCode"]/@content')
                ).strip()

                phone = "".join(
                    store_sel.xpath("//contact-module-responsive/@hotel-phone-number")
                ).strip()
                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"

                latitude = "".join(
                    store_sel.xpath(
                        '//div[@itemprop="geo"]/meta[@itemprop="latitude"]/@content'
                    )
                ).strip()
                longitude = "".join(
                    store_sel.xpath(
                        '//div[@itemprop="geo"]/meta[@itemprop="longitude"]/@content'
                    )
                ).strip()

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
