import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://myrosatis.com/locations/"
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
    urls = tree.xpath('//option[text()="Select a State"]/following-sibling::option')

    for url in urls:
        sub_page_url = "".join(url.xpath(".//@data-url"))

        session = SgRequests()
        r = session.get(sub_page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//article[@class="article-location"]')
        for d in div:
            page_url = "".join(d.xpath('.//a[./span[text()="View Details"]]/@href'))

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            ad = (
                "".join(
                    tree.xpath(
                        '//p[./strong[text()="Address"]]/following-sibling::p/text()'
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
            country_code = "USA"
            location_name = "".join(tree.xpath("//h1/text()")).strip()
            phone = (
                "".join(
                    tree.xpath(
                        '//p[./strong[text()="Phone"]]/following-sibling::p//text()'
                    )
                ).strip()
                or "<MISSING>"
            )
            latitude = (
                "".join(tree.xpath('//div[@class="map__inner"]/@data-lat'))
                or "<MISSING>"
            )
            longitude = (
                "".join(tree.xpath('//div[@class="map__inner"]/@data-lng'))
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[text()="Hours"]]/following-sibling::p//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if phone == "COMING SOON!":
                phone = "<MISSING>"
                hours_of_operation = "Coming Soon"
            if phone == "TEMPORARILY CLOSED" or phone == "Temporarily Closed":
                phone = "<MISSING>"
                hours_of_operation = "Temporarily Closed"
            if hours_of_operation.find("We will be closed ") != -1:
                hours_of_operation = hours_of_operation.split("We will be closed")[
                    0
                ].strip()
            if hours_of_operation.find("Kitchen Hours") != -1:
                hours_of_operation = hours_of_operation.split("Kitchen Hours")[
                    0
                ].strip()
            if page_url == "https://myrosatis.com/arcadia/":
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//p[./strong[text()="Hours"]]/following-sibling::div//p/text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
            hours_of_operation = (
                hours_of_operation.replace(
                    "Open for Carryout, Delivery and Patio Dining!", ""
                )
                .replace("Take Out, Delivery, Curbside Pickup & DoorDash", "")
                .strip()
            )
            if hours_of_operation.find("15%") != -1:
                hours_of_operation = hours_of_operation.split("15%")[0].strip()
            if hours_of_operation.find("No online orders 30") != -1:
                hours_of_operation = hours_of_operation.split("No online orders 30")[
                    0
                ].strip()
            if hours_of_operation.find("Last order") != -1:
                hours_of_operation = hours_of_operation.split("Last order")[0].strip()
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//p[./strong[text()="Hours"]]/following-sibling::*//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )

            if hours_of_operation.find("Delivery Fee: ") != -1:
                hours_of_operation = hours_of_operation.split("Delivery Fee: ")[
                    0
                ].strip()
            if hours_of_operation.find("Please note that") != -1:
                hours_of_operation = hours_of_operation.split("Please note that")[
                    0
                ].strip()
            if hours_of_operation.find("Minimum") != -1:
                hours_of_operation = hours_of_operation.split("Minimum")[0].strip()
            if hours_of_operation.find("May – October: ") != -1:
                hours_of_operation = hours_of_operation.split("May – October: ")[
                    0
                ].strip()
            if hours_of_operation.find("Text ") != -1:
                hours_of_operation = hours_of_operation.split("Text ")[0].strip()
            if hours_of_operation.find("*No") != -1:
                hours_of_operation = hours_of_operation.split("*No")[0].strip()

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
    locator_domain = "https://myrosatis.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
