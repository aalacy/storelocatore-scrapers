import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgselenium.sgselenium import SgFirefox
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.erewhonmarket.com"
    page_url = "https://www.erewhonmarket.com/locations"
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
    with SgFirefox() as fox:
        fox.get(page_url)
        a = fox.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//div[@class="locations-list-item"]')
        for d in div:
            location_name = "".join(d.xpath(".//h4/text()"))
            ad = (
                "".join(d.xpath('.//a[@class="address"]/text()'))
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
            phone = (
                "".join(d.xpath('.//a[@class="phone-number"]/text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = "<INACCESSIBLE>"
            key = (
                "".join(
                    tree.xpath(
                        "//style[@data-vue-ssr-id]/following-sibling::link[1]/@href"
                    )
                )
                .split("static/")[1]
                .split("/")[0]
                .strip()
            )
            session = SgRequests()
            r = session.get(
                f"https://www.erewhonmarket.com/_nuxt/static/{key}/locations/state.js"
            )

            latitude = (
                r.text.split(f"{street_address}")[1]
                .split("lat:")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                r.text.split(f"{street_address}")[1]
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
                phone=phone,
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
