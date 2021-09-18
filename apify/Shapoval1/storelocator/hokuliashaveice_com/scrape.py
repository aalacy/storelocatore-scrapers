import usaddress
import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://hokuliashaveice.com"
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

    r = session.get("https://hokuliashaveice.com/locations/", headers=headers)
    tree = html.fromstring(r.text)
    block = (
        "".join(tree.xpath('//script[contains(text(), "var features")]/text()'))
        .split("LatLng(33.9289171, -116.8158445),")[1]
        .split("];")[0]
    )
    block = "[" + block.replace("message:", "[").replace("),", ")],") + "]]"
    block = (
        block.replace("{", "")
        .replace("}", "")
        .replace("position:", '"')
        .replace(")]", '"]')
    )

    block = eval(block)

    for b in block:
        a = b[0]

        ad = html.fromstring(a)
        location_name = " ".join(ad.xpath("//*//text()[1]"))
        if location_name == "Year Round Catering":
            continue
        page_url = "https://hokuliashaveice.com/locations/"
        street_address = " ".join(ad.xpath("//*//text()[2]"))

        csz = " ".join(ad.xpath("//*//text()[3]")).replace("sdfasdf", "") or "<MISSING>"
        if (
            location_name.find("Desert Hills") != -1
            or location_name.find("Parker") != -1
            or location_name.find("Magnolia") != -1
            or location_name == "Spring"
            or location_name.find("Pleasant Grove") != -1
            or location_name.find("Riverdale ") != -1
            or location_name.find("St. George") != -1
            or location_name.find("West Valley") != -1
        ):
            street_address = " ".join(ad.xpath("//*//text()[3]"))
            csz = " ".join(ad.xpath("//*//text()[4]"))
        if location_name.find("Year Round Catering") != -1:
            street_address = "<MISSING>"
            csz = " ".join(ad.xpath("//*//text()[2]"))
        if (
            location_name.find("American Fork") != -1
            or location_name.find("Farmington") != -1
        ):
            csz = " ".join(ad.xpath("//*//text()[4]"))
        if csz.find("Mon-Sat") != -1:
            csz = "<MISSING>"
        if location_name.find("Kaysville") != -1:
            csz = " ".join(ad.xpath("//*//text()[4]"))

        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"

        if csz != "<MISSING>":
            aa = usaddress.tag(csz, tag_mapping=tag)[0]
            city = aa.get("city") or "<MISSING>"
            state = aa.get("state") or "<MISSING>"
            postal = aa.get("postal") or "<MISSING>"
        if location_name.find("Hokulia Cedar Hills") != -1:
            csz = " ".join(ad.xpath("//*//text()[4]"))
            city = csz.split(",")[0].strip()
            state = csz.split(",")[1].strip()

        if street_address.find("135 E Main St. ") != -1:
            city = "Am Fork"
            state = "UT"
            postal = "84003"

        if location_name.find("Cottonwood Heights") != -1:
            city = "Cottonwood Heights"
            state = "UT"

        if location_name.find("Columbia") != -1:
            street_address = " ".join(ad.xpath("//*//text()[2]")).split(",")[0].strip()
            city = " ".join(ad.xpath("//*//text()[2]")).split(",")[1].strip()
            state = (
                " ".join(ad.xpath("//*//text()[2]")).split(",")[2].split()[0].strip()
            )
            postal = (
                " ".join(ad.xpath("//*//text()[2]")).split(",")[2].split()[1].strip()
            )
        if location_name == "Prosper":
            adr = street_address
            street_address = adr.split(",")[0].strip()
            city = adr.split(",")[1].split()[0].strip()
            state = adr.split(",")[1].split()[1].strip()
            postal = adr.split(",")[1].split()[2].strip()
        if street_address.find("Stars Recreation Center - ") != -1:
            street_address = street_address.replace(
                "Stars Recreation Center - ", ""
            ).strip()
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        street_address = street_address.replace(",", "").strip()
        if street_address == "2929 FM 1960 Houston TX 77073":
            city = street_address.split()[3].strip()
            state = street_address.split()[4].strip()
            postal = street_address.split()[-1].strip()
            street_address = " ".join(street_address.split()[:-3])
        country_code = "US"

        latitude = (
            "".join(tree.xpath('//script[contains(text(), "var features = [")]/text()'))
            .split(f"{location_name}")[0]
            .split("position: new google.maps.LatLng(")[-1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "var features = [")]/text()'))
            .split(f"{location_name}")[0]
            .split("position: new google.maps.LatLng(")[-1]
            .split(",")[1]
            .replace(")", "")
            .strip()
        )

        location_type = "<MISSING>"
        hours_of_operation = ad.xpath("//*//text()")
        hours_of_operation = hours_of_operation[-3:]
        if (
            "Call for hours " in hours_of_operation
            or "Check for Seasonal Hours" in hours_of_operation
            or "Check for seasonal hours" in hours_of_operation
        ):
            hours_of_operation = "<MISSING>"
        if (
            location_name.find("Temecula") != -1
            or location_name.find("Grand Junction") != -1
            or location_name == "Draper"
            or location_name == "Sandy"
        ):
            hours_of_operation = " ".join(hours_of_operation[-2:])
        if (
            location_name.find("Vacaville") != -1
            or location_name == "Columbia"
            or location_name == "Magnolia"
            or location_name == "Spring"
            or location_name == "Moab"
            or location_name == "South Jordan"
            or location_name == "Tooele"
        ):
            hours_of_operation = "".join(hours_of_operation[-1])
        if location_name == "East Milkcreek":
            hours_of_operation = " ".join(hours_of_operation)
        if type(hours_of_operation) == list:
            hours_of_operation = "<MISSING>"
        hours_of_operation = hours_of_operation.replace("Hours", "").strip()
        ph = b[0]
        phone_list = re.findall(
            re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), ph
        )
        phone = "".join(phone_list) or "<MISSING>"
        if phone.find("0988832") != -1:
            phone = phone.split("0988")[0] + "0988"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        cms = (
            "".join(
                tree.xpath(
                    f'//div[contains(text(), "{location_name}")]/a[1]/div/strong/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if cms == "Coming soon":
            location_type = "Coming soon"
        try:
            adr = (
                "".join(
                    tree.xpath(f'//div[contains(text(), "{location_name}")]/a/@href')
                )
                .split("place/")[1]
                .split("/@")[0]
                .replace("+", " ")
                .strip()
            )
        except:
            adr = "<MISSING>"

        if (
            adr.find("1602 W Brandon") != -1
            or adr.find("4057 E County Hwy 30A") != -1
            or adr.find("4155 N Yellowstone Hwy") != -1
            or adr.find("986 Shepard") != -1
            or adr.find("170 W 200 N") != -1
            or adr.find("411 W 1425 N") != -1
            or adr.find("1875 7000 S") != -1
        ):
            postal = adr.split()[-1].strip()

        tmpcls = (
            "".join(tree.xpath(f'//div[contains(text(), "{location_name}")]/a//text()'))
            .replace("\n", "")
            .strip()
        )
        if tmpcls == "Closed for the season":
            hours_of_operation = "Temporarily closed"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
