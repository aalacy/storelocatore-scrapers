import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.angrycrabshack.com"

    api_url = "https://www.angrycrabshack.com/locations"
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
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[./p[@class="webpage"]]')
    for b in block:

        slug = "".join(b.xpath('.//a[contains(text(), "Webpage")]/@href'))
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = (
            "".join(tree.xpath("//h1/text()"))
            + "".join(tree.xpath('//h3[@class="alt slider"]/text()'))
            .replace("  ", " ")
            .replace("\n", "")
            .strip()
        )
        adr = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Address")]/following-sibling::p[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = usaddress.tag(adr, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        text = "".join(tree.xpath('//iframe[@loading="lazy"]/@data-lazy-src'))
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
        country_code = "US"
        state = a.get("state")
        postal = a.get("ZipCode")
        city = a.get("city")
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Hours")]/following-sibling::p//text() | //h3[contains(text(), "Hours")]/following-sibling::div/span/text()'
                )
            )
            .replace("\n", "")
            .strip()
        ) or "<MISSING>"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                "".join(
                    tree.xpath(
                        '//p[./strong[text()="Regular Hours"]]/following-sibling::p/text()'
                    )
                )
                or "<MISSING>"
            )
        tmphours = (
            " ".join(
                tree.xpath(
                    '//p[./em/strong[text()="TEMPORARY HOURS"]]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .split("Regular Hours")[0]
            .strip()
        )
        if tmphours:
            hours_of_operation = tmphours
        if page_url == "https://www.angrycrabshack.com/litchfield-rd-goodyear-az/":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h3[contains(text(), "Hours")]/following-sibling::*//text()'
                    )
                )
                .replace("\n", "")
                .split("TEMPORARY HOURS")[1]
                .split("REGULAR HOURS")[0]
                .strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("(TEMPORARILY)", "")
            .replace("\r\n", " ")
            .replace("\n", " ")
            .strip()
        )
        phone = (
            " ".join(
                tree.xpath(
                    '//div[./h3[text()="Location Info"]]//a[contains(@href, "tel")]/text()'
                )
            )
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h3[./strong[text()="Hours"]]/following-sibling::p/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        hours_of_operation = hours_of_operation.replace("Temporary Hours", "").strip()
        if hours_of_operation.find("Open") != -1:
            hours_of_operation = hours_of_operation.split("Open")[0].strip()

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
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
