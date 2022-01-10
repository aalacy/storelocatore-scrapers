import json
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.squeezein.com/"
    api_url = "https://www.squeezein.com/"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//figure[contains(@class, "image-figure")]')
    for d in div:

        page_url = "".join(d.xpath("./a/@href")) or "<MISSING>"
        img = "".join(d.xpath(".//img/@data-src"))
        if page_url == "<MISSING>" and img.find("Eagle") != -1:
            page_url = "https://www.squeezein.com/new-page"
        if page_url.find("http") == -1:
            page_url = f"https://www.squeezein.com{page_url}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h1[@class="page-title"]/text()')) or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = "".join(tree.xpath("//h2//text()")).strip()
        ad = (
            " ".join(tree.xpath('//div[@class="page-description"]/*[1]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if (
            page_url == "https://www.squeezein.com/carson-nv"
            or page_url == "https://www.squeezein.com/chinohills-ca-1/"
        ):
            ad = (
                " ".join(tree.xpath('//div[@class="page-description"]/p[2]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if page_url == "https://www.squeezein.com/fredericksburg-tx":
            ad = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Open 7")]]/preceding-sibling::p[position()<3]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if page_url == "https://www.squeezein.com/new-page":
            ad = (
                " ".join(tree.xpath("//h2/following-sibling::p[2]/text()"))
                .replace("\n", "")
                .strip()
            )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        ll1 = (
            "".join(
                tree.xpath(
                    '//div[@class="sqs-block map-block sqs-block-map sized vsize-12"]/@data-block-json'
                )
            )
            or "<MISSING>"
        )
        ll2 = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = ll2.split("!3d")[1].strip().split("!")[0].strip()
            longitude = ll2.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if ll1 != "<MISSING>":
            js = json.loads(ll1)
            latitude = js.get("location").get("mapLat") or "<MISSING>"
            longitude = js.get("location").get("mapLng") or "<MISSING>"

        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath('//*[contains(text(), "Phone:")]/text()'))
                .replace("Phone:", "")
                .strip()
            )
        if phone.count("(") > 1:
            phone = "(" + phone.split("(")[1].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[contains(text(), "Hours:")]/text() | //p[contains(text(), "HOURS:")]/text()'
                )
            )
            .replace("Hours:", "")
            .replace("HOURS:", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(tree.xpath('//*[contains(text(), "pm")]/text()'))
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
