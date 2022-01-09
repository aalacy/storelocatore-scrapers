import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.webuyanycarusa.com"
    api_url = "https://www.webuyanycarusa.com/locations"
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
    div = tree.xpath('//div[@class="branch-info"]')
    for d in div:
        slug = "".join(d.xpath(".//a/@href"))
        page_url = f"https://www.webuyanycarusa.com{slug}"
        location_name = "".join(d.xpath(".//a/text()"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            "".join(tree.xpath('//*[text()="Address:"]/following-sibling::text()'))
            .replace("\r\n", " ")
            .strip()
        )
        ad = " ".join(ad.split())
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        if city.find("Delray Beach") != -1:
            city = "Delray Beach"
        if city.find("Hudson") != -1:
            city = "Hudson"
        if city.find("Rocky Mount") != -1:
            city = "Rocky Mount"
        if city.find("Rock Hill") != -1:
            city = "Rock Hill"
        latitude = (
            "".join(
                tree.xpath('//script[contains(text(), "WBAC.BranchMap.Render")]/text()')
            )
            .split("WBAC.BranchMap.Render(")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                tree.xpath('//script[contains(text(), "WBAC.BranchMap.Render")]/text()')
            )
            .split("WBAC.BranchMap.Render(")[1]
            .split(",")[1]
            .strip()
        )
        phone = (
            "".join(tree.xpath('//*[text()="Phone:"]/following-sibling::a/text()'))
            .replace("\r\n", " ")
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//*[text()="Branch Hours"]/following-sibling::table//tr/td/text()'
                )
            )
            .replace("\r\n", " ")
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
