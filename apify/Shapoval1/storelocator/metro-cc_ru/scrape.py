from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.metro-cc.ru/"
    api_url = "https://www.metro-cc.ru/sobstvennye-torgovye-marki?from=under_search"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="m-select-options"]/button')
    for d in div:
        slug = "".join(d.xpath(".//@value"))
        if not slug:
            continue
        session = SgRequests()
        r = session.get(
            f"https://www.metro-cc.ru/services/saleline/store/get/{slug}?language=ru-RU",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        page_url = "".join(
            tree.xpath('//strong[@class="brandbar-popover-store-storename"]/a/@href')
        )
        location_name = (
            "".join(
                tree.xpath(
                    '//strong[@class="brandbar-popover-store-storename"]/a/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(tree.xpath('//a[@class="phone"]/text()')).replace("\n", "").strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//table[@class="table-text opening-hours"]//tr[2]/td//text()'
                )
            )
            .replace("\r\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        latitude = "".join(tree.xpath('//meta[@itemprop="latitude"]/@content'))
        longitude = "".join(tree.xpath('//meta[@itemprop="longitude"]/@content'))
        street_address = (
            "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
            .replace("\r\n", "")
            .strip()
        )
        street_address = " ".join(street_address.split()).strip()
        postal = (
            "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
            .replace("\r\n", "")
            .strip()
        )
        postal = " ".join(postal.split()).strip()
        country_code = "RU"
        city = (
            "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
            .replace("\r\n", "")
            .strip()
        )
        city = " ".join(city.split()).strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
