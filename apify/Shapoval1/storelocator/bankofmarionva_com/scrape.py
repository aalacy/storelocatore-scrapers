import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bankofmarionva.com"
    api_url = "https://www.bankofmarionva.com/"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//a[contains(text(), "Locations")]/following-sibling::ul/li/ul/li/a'
    )

    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1//text()"))
        info = tree.xpath("//h1/following::address[1]//text()")
        info = list(filter(None, [a.strip() for a in info]))
        ad = (" ".join(info).split("Telephone")[0].strip()) or "<MISSING>"
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        '//div[@class="col-md-6 col-1"]/p/text()[position() < 3]'
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
        country_code = "US"
        postal = a.get("postal") or "<MISSING>"
        try:
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "myLatLng ")]/text()'))
                .split("lat:")[1]
                .split(",")[0]
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "myLatLng ")]/text()'))
                .split("lng:")[1]
                .split("}")[0]
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//strong[contains(text(), "Office Hours")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("Our") != -1:
            hours_of_operation = hours_of_operation.split("Our")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace("(", "").replace(")", "").strip()
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h3[./strong[text()="Office Hours:"]]/following-sibling::p[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

        phone = "<MISSING>"
        for i in info:
            if "elephone" in i:
                phone = "".join(i).replace("Telephone:", "").strip()
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath('//div[@class="col-md-6 col-1"]/p/text()[last()]'))
                .split(":")[1]
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
