import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_urls():
    r = session.get("https://www.foxspizza.com/store-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//loc/text()")


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

    try:
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = SgRecord.MISSING
        city = a.get("city") or ""
        state = a.get("state")
        postal = a.get("postal")
    except usaddress.RepeatedLabelError:
        adr = line.split(",")
        street_address = adr.pop(0).strip()
        city = adr.pop(0).strip() or ""
        ad = adr.pop(0).strip()
        state, postal = ad.split()

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    for page_url in urls:
        if "%" in page_url:
            continue
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h5[@class='blog_title']//text()")).strip()
        raw_address = "".join(tree.xpath("//h6[@class='loc_address']/text()")).strip()
        if not raw_address:
            continue

        street_address, city, state, postal = get_address(raw_address)
        if "," in city:
            city = city.split(",")[0].strip()
            street_address = raw_address.split(city)[0].strip()
        if not city:
            city = location_name.split(",")[0].strip()
        phone = "".join(tree.xpath("//span[@class='phone_no']/a/text()")).strip()
        text = "".join(
            tree.xpath("//script[contains(text(), 'var locations =')]/text()")
        )
        try:
            text = text.split("var locations = [")[1].split("];")[0].strip()[:-1]
            geo = eval(text)
            latitude = geo[-3]
            longitude = geo[-2]
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        hours_of_operation = ";".join(tree.xpath("//span[@class='ad1']/text()"))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.foxspizza.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
