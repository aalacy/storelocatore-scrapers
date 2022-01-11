import time
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.richersounds.com"
    api_url = "https://www.richersounds.com/storefinder"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./a[contains(text(), "Get Directions")]]')
    for d in div:

        page_url = "".join(d.xpath(".//a[./img]/@href"))
        street_address = (
            "".join(d.xpath('.//span[@class="street"]/text()'))
            .replace("\n", "")
            .strip()
        )
        state = "".join(d.xpath(".//preceding::h2[1]/text()"))
        country_code = "UK"
        city = (
            "".join(d.xpath('.//span[@class="city"]/text()')).replace("\n", "").strip()
        )
        location_name = "Richer Sounds " + city
        phone = (
            "".join(d.xpath('.//a[@class="store-phone"]/text()'))
            .replace("\n", "")
            .strip()
        )
        time.sleep(10)
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        postal = (
            "".join(tree.xpath('//span[@class="post-code"]/text()'))
            .replace("\n", "")
            .strip()
        )
        map_js = "".join(
            tree.xpath('//div[@class="store-info-map js-store-map"]/@data-mage-init')
        )
        js = json.loads(map_js)
        latitude = js.get("storeMap").get("latitude")
        longitude = js.get("storeMap").get("longitude")
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="day"]/p[./span]/span/text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
