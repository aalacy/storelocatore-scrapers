import json
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bobmillsfurniture.com/"
    api_url = "https://www.bobmillsfurniture.com/api/rest/pages/"
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
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    jsblock = (
        "".join(tree.xpath("//*//text()")).replace("['", "").replace("']", "").strip()
    )
    js = json.loads(jsblock)

    for j in js:
        slug = "".join(j.get("request_url"))
        if not slug or slug.find("locations") == -1:
            continue
        page_url = f"https://www.bobmillsfurniture.com/{slug}"
        if page_url.find("distribution-center") != -1:
            continue

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath(
                '//h1/text() | //h1[@class="avb-typography__heading avb-typography__heading--title"]/span[1]/text()'
            )
        ).strip()
        ad = (
            " ".join(
                tree.xpath(
                    '//div[contains(@class, "address")]/span/text() | //span[@class="avb-typography__heading-line dsg-tools-main-paragraph dsg-tools-color-dark dsg-block-26__heading-line-2"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if ad.find("see you at") != -1:
            ad = ad.split("see you at")[1].strip()
        ad = " ".join(ad.split())

        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(tree.xpath('//*[contains(@data-href, "tel")]/text()'))
            .replace("Call Now", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[text()="Store Hours"]/following-sibling::ul[1]/li/text() | //h3[./span[contains(text(), "Store Hours ")]]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        cms = "".join(tree.xpath('//span[contains(text(), "Opening Soon ")]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"

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


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
