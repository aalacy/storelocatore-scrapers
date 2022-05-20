from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def get_tree(url):
    r = session.get(url, headers=headers)
    return html.fromstring(r.content)


def get_urls():
    root = get_tree("https://www.daiso-sangyo.co.jp/shop")
    return root.xpath("//li[@class='shop-pref-subList__item']/a/@href")


def get_data(slug, sgw: SgWriter):
    for i in range(1, 500):
        api = f"{slug}/page/{i}"
        tree = get_tree(api)
        divs = tree.xpath("//li[@class='resultList-item']")

        for d in divs:
            page_url = "".join(d.xpath(".//a[@class='resultList-item-link']/@href"))
            location_name = "".join(
                d.xpath(".//h2[@class='resultList-item-name']/text()")
            ).strip()
            location_type = "".join(
                d.xpath(".//div[@class='resultList-item-category_wrap']/span/text()")
            )
            raw_address = " ".join(
                "".join(
                    d.xpath(
                        ".//dt[contains(text(), '住所')]/following-sibling::dd//text()"
                    )
                ).split()
            )
            street_address, city, state, postal = get_international(raw_address)
            phone = (
                " ".join(
                    "".join(
                        d.xpath(
                            ".//dt[contains(text(), '電話番号')]/following-sibling::dd//text()"
                        )
                    ).split()
                )
                .replace("－", "")
                .strip()
            )

            text = "".join(d.xpath(".//a[contains(@href, 'lat=')]/@href"))
            try:
                latitude = text.split("lat=")[1].split("&")[0]
                longitude = text.split("lon=")[1].split("&")[0]
            except:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
            hours_of_operation = "".join(
                d.xpath(".//dt[contains(text(), '営業時間')]/following-sibling::dd/text()")
            ).strip()

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="JP",
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)

        if len(divs) < 10:
            break


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.daiso-sangyo.co.jp/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
