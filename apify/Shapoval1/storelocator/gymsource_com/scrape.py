import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():

    r = session.get("https://www.gymsource.com/sitemap.xml")
    tree = html.fromstring(r.content)
    return tree.xpath(
        "//url/loc[contains(text(), 'https://www.gymsource.com/store-locator/')]/text()"
    )


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.gymsource.com"
    page_url = "".join(url)

    if len(page_url) < 43:
        return

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
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = (
        " ".join(
            tree.xpath(
                "//h2[contains(text(), 'Address')]/following-sibling::p[1]/text()"
            )
        )
        .replace("\n", "")
        .strip()
    )
    line = " ".join(line.split())
    if line.find("Forums at Peachtree") != -1:
        line = line.split("Forums at Peachtree")[1].strip()
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    if not street_address:
        return
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")
    country_code = "US"
    location_name = "".join(tree.xpath("//h1/text()"))
    phone = (
        "".join(
            tree.xpath(
                "//h3[contains(text(), 'Contact')]/following-sibling::p[1]/text()"
            )
        )
        .replace("\n", "")
        .strip()
    )
    if phone.find("GYM SOURCE") != -1:
        phone = "<MISSING>"
    latitude = "".join(tree.xpath("//geo-map/@lat"))
    longitude = "".join(tree.xpath("//geo-map/@lng"))
    hours_of_operation = (
        " ".join(tree.xpath("//table/tbody/tr/td/text()"))
        .replace("\n", "")
        .replace("   ", " ")
        .strip()
    )

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
        raw_address=line,
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
