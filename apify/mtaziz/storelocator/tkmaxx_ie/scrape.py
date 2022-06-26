from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger(logger_name="tkmaxx_ie")
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def get_urls():
    with SgRequests() as http:
        r = http.get("https://www.tkmaxx.ie/sitemap")
        tree = html.fromstring(r.text)

        return tree.xpath(
            "//a[@class='top-right-store-locator-link']/following-sibling::ul//a/@href"
        )


def scrape_until_all_stores_fetched(urls, items):
    if not urls:
        return
    else:
        logger.info(f"urls: {urls}")
        logger.info(f"urls: {urls[0]}")
        slug = urls[0]
        page_url = f"https://www.tkmaxx.ie{slug}"
        with SgRequests() as session:
            try:
                r = session.get(page_url, headers=headers)
                logger.info(f"HTTPStatusCode: {r.status_code}")
                tree = html.fromstring(r.text)
                d = tree.xpath("//div[@class='nearby-store active-store']")[0]
                location_name = "".join(d.xpath("./a/text()")).strip()
                if location_name:
                    urls.remove(slug)
                    raw_address = " ".join(
                        " ".join(
                            d.xpath("//address[@itemprop='address']//text()")
                        ).split()
                    )
                    page_url = "https://www.tkmaxx.ie" + "".join(d.xpath("./a/@href"))
                    store_number = "".join(d.xpath("./@data-store-id"))
                    latitude = "".join(d.xpath("./@data-latitude"))
                    longitude = "".join(d.xpath("./@data-longitude"))
                    b = d.xpath("./following-sibling::div[1]")[0]
                    street_address = "".join(
                        b.xpath(".//p[@itemprop='streetAddress']/text()")
                    ).strip()
                    city = location_name
                    if "(" in city:
                        city = city.split("(")[0].strip()
                    postal = "".join(
                        b.xpath(".//p[@itemprop='zipCode']/text()")
                    ).strip()
                    phone = "".join(
                        b.xpath(".//p[@itemprop='telephone']/text()")
                    ).strip()
                    logger.info(f"Phone: {phone}")
                    hours_of_operation = "".join(
                        b.xpath(".//span[@itemprop='openingHours']/text()")
                    ).strip()
                    if "Bank" in hours_of_operation:
                        hours_of_operation = hours_of_operation.split("Bank")[0].strip()

                    row = SgRecord(
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=SgRecord.MISSING,
                        zip_postal=postal,
                        country_code="IE",
                        store_number=store_number,
                        phone=phone,
                        location_type=SgRecord.MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        locator_domain="tkmaxx.ie",
                        raw_address=raw_address,
                        hours_of_operation=hours_of_operation,
                    )
                    logger.info(f"Row as dict: {row.as_dict()}")
                    if row.as_dict() not in items:
                        items.append(row.as_dict())
                        scrape_until_all_stores_fetched(urls, items)
                else:
                    scrape_until_all_stores_fetched(urls, items)
            except:
                try:
                    r = session.get(page_url, headers=headers)
                    logger.info(f"HTTPStatusCode: {r.status_code}")
                    tree = html.fromstring(r.text)
                    d = tree.xpath("//div[@class='nearby-store active-store']")[0]
                    location_name = "".join(d.xpath("./a/text()")).strip()
                    if location_name:
                        urls.remove(slug)
                        raw_address = " ".join(
                            " ".join(
                                d.xpath("//address[@itemprop='address']//text()")
                            ).split()
                        )
                        page_url = "https://www.tkmaxx.ie" + "".join(
                            d.xpath("./a/@href")
                        )
                        store_number = "".join(d.xpath("./@data-store-id"))
                        latitude = "".join(d.xpath("./@data-latitude"))
                        longitude = "".join(d.xpath("./@data-longitude"))
                        b = d.xpath("./following-sibling::div[1]")[0]
                        street_address = "".join(
                            b.xpath(".//p[@itemprop='streetAddress']/text()")
                        ).strip()
                        city = location_name
                        if "(" in city:
                            city = city.split("(")[0].strip()
                        postal = "".join(
                            b.xpath(".//p[@itemprop='zipCode']/text()")
                        ).strip()
                        phone = "".join(
                            b.xpath(".//p[@itemprop='telephone']/text()")
                        ).strip()
                        logger.info(f"Phone: {phone}")
                        hours_of_operation = "".join(
                            b.xpath(".//span[@itemprop='openingHours']/text()")
                        ).strip()
                        if "Bank" in hours_of_operation:
                            hours_of_operation = hours_of_operation.split("Bank")[
                                0
                            ].strip()

                        row = SgRecord(
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=SgRecord.MISSING,
                            zip_postal=postal,
                            country_code="IE",
                            store_number=store_number,
                            phone=phone,
                            location_type=SgRecord.MISSING,
                            latitude=latitude,
                            longitude=longitude,
                            locator_domain="tkmaxx.ie",
                            raw_address=raw_address,
                            hours_of_operation=hours_of_operation,
                        )
                        logger.info(f"Row as dict: {row.as_dict()}")
                        if row.as_dict() not in items:
                            items.append(row.as_dict())
                            scrape_until_all_stores_fetched(urls, items)
                    else:
                        scrape_until_all_stores_fetched(urls, items)
                except:
                    raise Exception(f"Please Fix FetchingRecordError | {page_url} ")

    return items


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    data = scrape_until_all_stores_fetched(urls[0:], [])
    logger.info(f"Data: {data}")
    if data is not None:
        for item in data:
            rec = SgRecord(
                locator_domain=item["locator_domain"],
                page_url=item["page_url"],
                location_name=item["location_name"],
                street_address=item["street_address"],
                city=item["city"],
                state=item["state"],
                zip_postal=item["zip"],
                country_code=item["country_code"],
                store_number=item["store_number"],
                phone=item["phone"],
                location_type=item["location_type"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                hours_of_operation=item["hours_of_operation"],
                raw_address=item["raw_address"],
            )

            sgw.write_row(rec)


if __name__ == "__main__":
    locator_domain = "https://www.tkmaxx.ie/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
