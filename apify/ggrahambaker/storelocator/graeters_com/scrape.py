import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.graeters.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), '/retail-stores/')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "http://graeters.com/"
    page_url = url

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
    ad = "".join(tree.xpath('//address[@class="location-address"]/text()'))
    if page_url == "https://www.graeters.com/stores/retail-stores/louisville/ferncreek":
        ad = (
            "".join(tree.xpath('//p[contains(text(),"located at")]/text()'))
            .split("located at")[1]
            .split("and")[0]
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
    location_name = "".join(
        tree.xpath('//div[contains(@class, "location-details")]//h1//text()')
    )
    phone = "".join(tree.xpath('//a[@class="location-phone"]/text()')) or "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//span[text()="Get Directions"]/preceding::ul[1]/li/text() | //span[text()="Get it delivered now"]/preceding::ul[1]/li/text() | //span[text()="Get it delivered now with Uber Eats"]/preceding::ul[1]/li/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )

    try:
        latitude = (
            "".join(tree.xpath('//a[text()="Get Directions"]/@href'))
            .split("/")[-1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//a[text()="Get Directions"]/@href'))
            .split("/")[-1]
            .split(",")[1]
            .strip()
        )
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    p_closed = "".join(tree.xpath('//strong[text()="PERMANENTLY CLOSED"]/text()'))
    if p_closed:
        return

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
        raw_address=ad,
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
