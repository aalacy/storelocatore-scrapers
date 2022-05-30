import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.safelite.com/store-locator/store-locations-by-state")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='state-store-list']/a/@href")


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
    try:
        a = usaddress.tag(line, tag_mapping=tag)[0]
        adr1 = a.get("address1") or ""
        adr2 = a.get("address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city") or SgRecord.MISSING
        state = a.get("state") or SgRecord.MISSING
        postal = a.get("postal")
    except usaddress.RepeatedLabelError:
        a = line.split(", ")
        state, postal = a.pop().split()
        city = a.pop()
        street_address = ", ".join(a)

    return street_address, city, state, postal


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.safelite.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    if location_name == "Locations":
        return

    raw_address = "".join(
        tree.xpath("//h2[@class='shop-address']/following-sibling::p/text()")
    ).strip()
    street_address, city, state, postal = get_address(raw_address)
    if city == SgRecord.MISSING and state == SgRecord.MISSING:
        try:
            city, state = location_name.split(", ")
        except:
            pass

    try:
        phone = "".join(
            tree.xpath(
                "//strong[contains(text(), 'call ') or contains(text(), '|')]/text()"
            )
        )
        phone = phone.split("|")[0].split("call")[1].strip()
    except IndexError:
        phone = SgRecord.MISSING

    latitude = "".join(tree.xpath("//div[@data-start-lat]/@data-start-lat"))
    longitude = "".join(tree.xpath("//div[@data-start-lon]/@data-start-lon"))
    hours = tree.xpath(
        "//h2[contains(text(), 'Shop hours')]/following-sibling::p[1]/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

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
    locator_domain = "https://www.safelite.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
