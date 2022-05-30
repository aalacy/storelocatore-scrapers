import json
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
    r = session.get("https://gorefreshdental.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://gorefreshdental.com/"
    page_url = "".join(url)
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath("//h1//text()")).replace("\n", "").strip() or "<MISSING>"
    )
    if location_name == "<MISSING>":
        location_name = (
            "".join(
                tree.xpath(
                    '//h2[@class="coh-heading coh-style-heading-1-size"]//text()'
                )
            )
            or "<MISSING>"
        )
    street_address = (
        "".join(tree.xpath('//span[@class="address-line1"]/text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if street_address == "<MISSING>":
        return
    suite = (
        "".join(tree.xpath('//span[@class="address-line2"]/text()'))
        .replace("\n", "")
        .strip()
    )
    if suite:
        street_address = street_address + " " + suite
    state = (
        "".join(tree.xpath('//span[@class="administrative-area"]/text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath('//span[@class="postal-code"]/text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    country_code = (
        "".join(tree.xpath('//span[@class="country"]/text()')).replace("\n", "").strip()
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath('//span[@class="locality"]/text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    phone = (
        "".join(
            tree.xpath(
                '//div[@class="office-hours"]/following::a[contains(@href, "tel")][1]//text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if phone == "<MISSING>":
        phone = (
            "".join(
                tree.xpath(
                    '//h1/following::a[contains(@href, "tel")][1]//text() | //h3[./a[contains(@href, "tel")]]//a//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
    hours_of_operation = (
        " ".join(tree.xpath('//div[@class="office-hours__item"]//text()'))
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = "".join(
        tree.xpath('//script[@data-drupal-selector="drupal-settings-json"]/text()')
    )
    latlong = list(json.loads(js_block)["leaflet"].values())[0]["features"][0]
    latitude = latlong.get("lat")
    longitude = latlong.get("lon")

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


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
