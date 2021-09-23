import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.aussiegrill.com"
    api_url = "https://www.aussiegrill.com/scripts/locationData.json"
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
    js = r.json()

    for j in js:

        page_url = j.get("YextURL") or "https://www.aussiegrill.com/pickup.html"
        location_name = "".join(j.get("Name"))
        location_type = "<MISSING>"
        ad = "".join(j.get("Address"))
        locinfo = "".join(j.get("LocationInfo"))

        if locinfo.find("Coming") != -1:
            continue
        phone = "".join(j.get("Phone")).replace("Call:", "").strip() or "<MISSING>"
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        city = "<MISSING>"
        if ad:
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            city = a.get("city") or "<MISSING>"
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        if location_name.find(",") != -1:
            city = location_name.split(",")[0].strip()
            state = location_name.split(",")[1].strip()
        HasPickup = j.get("HasPickup")
        HasDelivery = j.get("HasDelivery")
        if HasDelivery:
            location_type = "Delivery"
        if HasDelivery and HasPickup:
            location_type = "Delivery and Pickup"
        if location_type != "Delivery and Pickup":
            continue

        latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = "<MISSING>"
        if page_url != "https://www.aussiegrill.com/pickup.html":
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(tree.xpath('//table[@class="c-hours-details"]//tr/td//text()'))
                .replace("\n", "")
                .strip()
            )
            phone = (
                "".join(
                    tree.xpath(
                        '//h2[text()="Contact"]/following-sibling::div[1]//a[@class="Phone-link"]/text()'
                    )
                )
                or "<MISSING>"
            )
            latitude = (
                "".join(tree.xpath('//script[@class="js-map-data"]/text()'))
                .split('latitude":')[1]
                .split(",")[0]
            )

            longitude = (
                "".join(tree.xpath('//script[@class="js-map-data"]/text()'))
                .split('longitude":')[1]
                .split("}")[0]
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
