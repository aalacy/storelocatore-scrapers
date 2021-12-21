import usaddress
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
    r = session.get("https://www.anthonys.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), 'restaurant')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.anthonys.com"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    tree = html.fromstring(r.text)
    ad = " ".join(
        tree.xpath('//div[@class="left-column-content column-content"]/h3[1]/text()')
    ).replace("\n", "")
    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = (
        f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
        or "<MISSING>"
    )
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    country_code = "US"
    page_url = "".join(url)
    if page_url.find("https://www.anthonys.com/restaurants/") != -1:
        return
    location_name = (
        "".join(tree.xpath('//h2[@class="intro-content-title"]/text()')).strip()
        or "<MISSING>"
    )
    phone = (
        "".join(
            tree.xpath(
                '//h3[contains(text(), "Contact")]/following-sibling::p/a[contains(@href, "tel")]/text() | //h3[contains(text(), "Contact")]/following-sibling::p/text() | //h3[contains(text(), "Phone")]/following-sibling::p/a[contains(@href, "tel")]/text()'
            )
        ).strip()
        or "<MISSING>"
    )
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h3[contains(text(),"Hours")]/following-sibling::p[1]/text() | //h3[1][contains(text(),"Indoor Dining")]/following-sibling::p[1]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    ) or "<MISSING>"
    if hours_of_operation == "<MISSING>":
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//strong[contains(text(), "Hours")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
    if hours_of_operation.find("Coming soon") != -1:
        hours_of_operation = "Coming soon"
    if hours_of_operation.find("Closed for the season") != -1:
        hours_of_operation = "Temporarily closed"
    if hours_of_operation.find("Temporarily Closed") != -1:
        hours_of_operation = "Temporarily closed"
    if hours_of_operation.find("Anthony’s Cabana") != -1:
        hours_of_operation = "<MISSING>"
    if hours_of_operation.find("Not currently available.") != -1:
        hours_of_operation = "Closed"
    if street_address.find("1207") != -1:
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(),"Hours:")]/following-sibling::div[1]//text() | //strong[contains(text(),"Hours:")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        ) or "<MISSING>"

    if location_name.find("Anthony’s Cabana") != -1:
        hours_of_operation = "Closed"
    if page_url == "https://www.anthonys.com/restaurant/anthonys-beach-cafe/":
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//strong[contains(text(), "Anthony’s Beach Cafe Hours:")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
    if page_url == "https://www.anthonys.com/restaurant/anthonys-at-columbia-point/":
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(),"Hours:")]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
    if page_url == "https://www.anthonys.com/restaurant/dawg-boat-chinooks/":
        location_name = "".join(tree.xpath("//h1/text()"))
        city = "Seattle"
        state = "WA"
        phone = "".join(tree.xpath('//strong[contains(text(), "by calling")]/a/text()'))
        hours_of_operation = (
            "".join(
                tree.xpath('//strong[contains(text(), "by calling")]/text()[last()]')
            )
            .replace("\n", "")
            .strip()
        )
    hours_of_operation = hours_of_operation.replace(
        "Sundays  |  10am – 2pm", ""
    ).strip()

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
        latitude=SgRecord.MISSING,
        longitude=SgRecord.MISSING,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
