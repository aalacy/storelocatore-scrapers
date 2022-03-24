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
    r = session.get(
        "https://www.heartland.bank/LEARNING/FAQs/what-are-your-current-branch-locations-and-contact-information-for-them",
        headers=headers,
    )
    tree = html.fromstring(r.text)
    return tree.xpath('//div[@class="EDN_article_content"]//ul/li/p/a[1]/@href')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.heartland.bank/"
    page_url = "".join(url)
    if page_url.find("/Florida") != -1:
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }

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
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    ad = (
        " ".join(tree.xpath('//h4[text()="Address:"]/following-sibling::p[1]/text()'))
        .replace("(Rossmore Square Plaza)", "")
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
    location_name = "".join(tree.xpath("//h1/text()"))
    phone = (
        "".join(tree.xpath('//p[contains(text(), "Phone:")]/text()[1]'))
        .replace("Phone:", "")
        .strip()
    )
    latitude = (
        "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
        .split('"latitude":')[1]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
        .split('"longitude":')[1]
        .split("}")[0]
        .strip()
    )
    location_type = "Branch"
    hours_of_operation = (
        " ".join(
            tree.xpath('//p[text()="Lobby"]/following-sibling::table[1]//td/text()')
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if hours_of_operation == "<MISSING>":
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[text()="Lobby/Drive-Thru"]/following-sibling::table[1]//td/text()'
                )
            )
            .replace("\n", "")
            .strip()
        ) or "<MISSING>"
    if hours_of_operation == "<MISSING>":
        hours_of_operation = (
            " ".join(tree.xpath('//h4[text()="Hours"]/following-sibling::p[1]/text()'))
            .replace("\n", "")
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
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):

    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests(verify_ssl=False)
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
