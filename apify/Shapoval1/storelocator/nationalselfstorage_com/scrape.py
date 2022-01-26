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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get("https://www.nationalselfstorage.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath('//url/loc[contains(text(), "/storage-units/")]/text()')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.nationalselfstorage.com"
    page_url = url
    if (
        page_url
        == "https://www.nationalselfstorage.com/storage-units/texas/horizon-city/elp5-379005/"
        or page_url
        == "https://www.nationalselfstorage.com/storage-units/texas/el-paso/"
    ):
        return

    session = SgRequests()
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath('//h2[@id="target-focus"]/text()')) or "<MISSING>"
    )
    if location_name == "<MISSING>":
        location_name = (
            " ".join(
                tree.xpath(
                    '//h2[@class="elementor-heading-title elementor-size-default"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
    ad = (
        "".join(
            tree.xpath(
                '//div[@class="facility-address"]/text() | //div[contains(text(), "Dr.")]//text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    country_code = "US"
    if location_name.find("Tucson") != -1:
        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[1].strip()
    phone = (
        "".join(
            tree.xpath(
                '//span[./span[@class="ss-icon icon-ss-phone"]]/following-sibling::a//text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if phone == "<MISSING>":
        phone = (
            "".join(tree.xpath('//div[@id="inss_phone"]//*//text()'))
            .replace("\n", "")
            .strip()
        )
        phone = " ".join(phone.split())

    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//div[@class="gate-hours"]/div/div/text() | //strong[contains(text(), "ACCESS")]/text()'
            )
        )
        .replace("\n", "")
        .replace("ACCESS:", "")
        .strip()
        or "<MISSING>"
    )
    if hours_of_operation == "<MISSING>":
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="business-hours-row"]/div/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
    if hours_of_operation.count("Open 24h") == 7:
        hours_of_operation = "Open 24h"
    ll = "".join(tree.xpath("//img/@data-src")) or "<MISSING>"
    try:
        latitude = ll.split("markers=")[1].split(",")[0].strip()
        longitude = ll.split("markers=")[1].split(",")[1].split("h")[0].strip()
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"

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
        location_type=location_type,
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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
