import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://deseretbook.com/"
    api_url = "https://deseretbook.com/retail_stores"
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
    div = tree.xpath('//section[@id="sidebar"]//div[@class="store_list"]/div/a[1]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://deseretbook.com{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//address/h2/text()"))
        location_type = "Retail store"
        ad = (
            " ".join(tree.xpath('//a[@class="full-address"]/text()'))
            .replace("\n", "")
            .strip()
        )

        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        state = a.get("state")
        if city == "Spanish Fork UT":
            city = city.replace("UT", "").strip()
            state = "UT"
        postal = a.get("postal")
        country_code = "US"
        store_number = page_url.split("/")[-1].strip()
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "addDomListener")]/text()'))
            .split("dbMap.drawStoreMap(")[1]
            .split(",")[0]
            .strip()
            or "<MISSING>"
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "addDomListener")]/text()'))
            .split("dbMap.drawStoreMap(")[1]
            .split(",")[1]
            .strip()
            or "<MISSING>"
        )
        phone = (
            "".join(tree.xpath('//address//a[contains(@href, "tel")]/text()'))
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[text()="Store Hours"]/following-sibling::table[1]//tr/td/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
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
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
