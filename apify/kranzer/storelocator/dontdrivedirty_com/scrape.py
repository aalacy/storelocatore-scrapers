import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://dontdrivedirty.com/"
    api_url = "https://dontdrivedirty.com/locationsandpricing/"
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
    div = tree.xpath('//div[contains(@class, "single")]')
    for d in div:

        page_url = "".join(d.xpath('.//a[text()="See Details"]/@href'))
        location_name = "".join(d.xpath('.//p[@class="h5 mb-2"]/strong/text()')).strip()
        ad = (
            " ".join(d.xpath('.//strong[text()="Address: "]/following-sibling::text()'))
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
        try:
            latitude = (
                "".join(d.xpath('.//a[text()="Get Directions"]/@href'))
                .split("/")[-1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(d.xpath('.//a[text()="Get Directions"]/@href'))
                .split("/")[-1]
                .split(",")[1]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//strong[text()="Hours: "]/following-sibling::text()'))
            .replace("\n", "")
            .strip()
        )
        if latitude == "<MISSING>":
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            latitude = (
                "".join(tree.xpath('//script[contains(text(), "lat:")]/text()'))
                .split("lat:")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "lat:")]/text()'))
                .split("lng:")[1]
                .split("}")[0]
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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
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
