from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://storelocations.ae.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://ae.com/"
    page_url = url

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    street_address = (
        "".join(
            tree.xpath(
                '//address[@id="address"]//meta[@itemprop="streetAddress"]/@content'
            )
        )
        or "<MISSING>"
    )
    if street_address == "<MISSING>":
        return
    city = (
        "".join(
            tree.xpath(
                '//address[@id="address"]//span[@class="c-address-city"]//text()'
            )
        )
        or "<MISSING>"
    )
    state = (
        "".join(
            tree.xpath(
                '//address[@id="address"]//abbr[@class="c-address-state"]//text()'
            )
        )
        or "<MISSING>"
    )
    postal = (
        "".join(
            tree.xpath(
                '//address[@id="address"]//span[@class="c-address-postal-code"]//text()'
            )
        )
        or "<MISSING>"
    )
    country_code = "".join(tree.xpath('//address[@id="address"]/@data-country'))
    location_name = (
        " ".join(tree.xpath('//span[@id="location-name"]//text()'))
        .replace("\n", "")
        .strip()
    )
    location_name = " ".join(location_name.split())
    if "American Eagle" in location_name and "Aerie Outlet" in location_name:
        location_name = "American Eagle & Aerie Outlet"
    if "American Eagle" in location_name and "Aerie Store" in location_name:
        location_name = "American Eagle & Aerie"
    if "Aerie Outlet" in location_name and "American Eagle" not in location_name:
        location_name = "Aerie Outlet"
    if "Aerie Store" in location_name and "American Eagle" not in location_name:
        location_name = "Aerie"
    if "American Eagle Outlet" in location_name and "Aerie" not in location_name:
        location_name = "American Eagle Outlet"
    if "OFFLINE" in location_name:
        location_name = "OFFLINE"
    if "American Eagle Store" in location_name and "Aerie" not in location_name:
        location_name = "American Eagle"
    if "American Eagle Outfitters" in location_name and "Aerie" not in location_name:
        location_name = "American Eagle"
    if "Unsubscribed" in location_name:
        location_name = "Unsubscribed"
    phone = "".join(tree.xpath('//div[@itemprop="telephone"]//text()')) or "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//div[@class="c-hours"]//table[@class="c-hours-details"]//tr//td//text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = " ".join(hours_of_operation.split())
    try:
        store_number = (
            "".join(tree.xpath('//script[contains(text(), "ids")]/text()'))
            .split('"ids":')[1]
            .split(",")[0]
            .strip()
        )
    except:
        return
    if store_number == "null":
        store_number = "<MISSING>"
    latitude = "".join(tree.xpath("//div/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div/@data-long")) or "<MISSING>"

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
