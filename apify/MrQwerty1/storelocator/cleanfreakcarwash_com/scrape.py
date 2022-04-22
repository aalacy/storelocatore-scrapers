import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://cleanfreakcarwash.com/", headers=headers)
    tree = html.fromstring(r.text)

    return set(tree.xpath("//a[text()='LOCATIONS']/following-sibling::ul//a/@href"))


def get_address(line):
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
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def get_data(page_url, sgw: SgWriter):
    if not page_url.startswith("http"):
        return

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    location_name = "".join(
        tree.xpath(
            "//div[@data-slide-id='et_pb_slide_0']//h2[@class='et_pb_slide_title']//text()"
        )
    ).strip()
    raw_address = "".join(
        tree.xpath(
            "//div[@data-slide-id='et_pb_slide_0']//h2[@class='et_pb_slide_title']/following-sibling::div//h2//text()"
        )
    ).strip()
    street_address, city, state, postal = get_address(raw_address)

    try:
        text = "".join(tree.xpath("//iframe/@data-src|//iframe/@src"))
        latitude = text.split("!3d")[1].split("!")[0]
        longitude = text.split("!2d")[1].split("!")[0]
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    phone = tree.xpath("//a[contains(@href, 'tel:')]/@href")[0].replace("tel:", "")
    hours = "".join(
        tree.xpath(
            "//div[@data-slide-id='et_pb_slide_0']//strong[contains(text(), 'hours')]/text()|//div[@data-slide-id='et_pb_slide_0']//span[contains(text(), 'hours')]/text()|//div[@data-slide-id='et_pb_slide_0']//strong[contains(text(), 'PM')]/text()"
        )
    )
    hours_of_operation = hours.split("from")[-1].strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://cleanfreakcarwash.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
