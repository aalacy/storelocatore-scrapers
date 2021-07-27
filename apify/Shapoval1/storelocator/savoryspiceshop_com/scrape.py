import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://www.savoryspiceshop.com/locations"
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
    div = tree.xpath('//a[contains(@id, "store")]')

    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        if page_url.find("st. P") != -1:
            page_url = page_url.replace("st. Petersburg.html", "st.%20Petersburg.html")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = (
            "".join(tree.xpath('//h1[@style="font-weight: bold;"]//text()'))
            .replace("\n", "")
            .strip()
        )
        adr = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Address")]/following-sibling::p[1]/text()'
                )
            )
            .replace("Sonoma Market Place", "")
            .replace("Southlands Shopping Center", "")
            .replace("Atherton Mill", "")
            .replace("Birkdale Village", "")
            .replace("\n", "")
            .strip()
        )
        a = usaddress.tag(adr, tag_mapping=tag)[0]
        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "")
            .replace("Rockbrook Village", "")
            .replace("Lincoln Square", "")
            .strip()
        )

        phone = (
            "".join(
                tree.xpath(
                    '//h3[contains(text(), "Contact")]/following-sibling::p[1]/text()[1]'
                )
            )
            .replace("P:", "")
            .strip()
        )
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        if state.find("Fe, New Mexico") != -1:
            city = city + " " + state.split(",")[0].strip()
            state = state.replace("Fe,", "").strip()

        ll = (
            "".join(tree.xpath('//script[contains(text(), "googleMap")]/text()'))
            .split("center: '(")[1]
            .split(")',")[0]
            .strip()
        )

        latitude = ll.split(",")[0].strip()
        longitude = ll.split(",")[1].strip()
        if latitude == "0.0000000":
            latitude = "<MISSING>"
        if longitude == "0.0000000":
            longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Hours")]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("hours:") != -1:
            hours_of_operation = hours_of_operation.split("hours:")[1].strip()
        if hours_of_operation.find("Spice Experts.") != -1:
            hours_of_operation = hours_of_operation.split("Spice Experts.")[1].strip()
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        if hours_of_operation.find("We will be OPEN") != -1:
            hours_of_operation = hours_of_operation.split("We will be OPEN")[0].strip()
        if (
            hours_of_operation.find("or on our website.") != -1
            and hours_of_operation.find("908.264.8947") == -1
        ):
            hours_of_operation = hours_of_operation.split("or on our website.")[
                1
            ].strip()
        if hours_of_operation.find("HOLIDAY NOTICE:") != -1:
            hours_of_operation = hours_of_operation.split("HOLIDAY NOTICE:")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace("Curbside Pick Up Available", "")
            .replace("SPRING HOURS", "")
            .replace("?", "")
            .replace("STORE HOURS", "")
            .replace("(Closed Easter Sunday)", "")
            .replace("Curbside Pick Up available", "")
            .replace("SPRING/SUMMER HOURS", "")
            .strip()
        )
        if hours_of_operation.find("We can") != -1:
            hours_of_operation = hours_of_operation.split("We can")[0].strip()

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
    locator_domain = "https://www.savoryspiceshop.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
