import json
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jjfishandchicken.com/"
    api_url = "https://www.jjfishandchicken.com/locations/"
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
    div = tree.xpath(
        '//ul[@id="top-menu"]//a[text()="Locations"]/following-sibling::ul/li/a'
    )
    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("http") == -1:
            page_url = f"https://www.jjfishandchicken.com{page_url}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//*[@class="et_pb_module_header"]/text()'))
        ad = (
            " ".join(
                tree.xpath(
                    '//*[@class="et_pb_module_header"]/following-sibling::div[1]/p/span[1]/text() | //*[@class="et_pb_module_header"]/following-sibling::div[1]/span[1]/text()'
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
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        j = (
            "".join(tree.xpath('//script[contains(text(), "center_lat")]/text()'))
            .split(".maps(")[1]
            .split(").data")[0]
            .strip()
        )
        js = json.loads(j)
        latitude = js.get("places")[0].get("location").get("lat")

        longitude = js.get("places")[0].get("location").get("lng")
        if "," in longitude:
            longitude = "".join(longitude).split(",")[0].strip()
        phone = "".join(
            tree.xpath(
                '//div[@class="et_pb_team_member_description"]//a[contains(@href, "tel")]/text()'
            )
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//span[contains(text(), "Mon")]/text() | //p[.//a]/following-sibling::h5//text()'
                )
            )
            .replace("(7 days)", "")
            .replace("Open", "")
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
