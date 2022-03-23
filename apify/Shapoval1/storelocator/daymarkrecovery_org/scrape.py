import json
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.daymarkrecovery.org"
    api_url = "https://www.daymarkrecovery.org/locations"

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
    jsblock = "".join(tree.xpath('//script[contains(text(), "markers")]/text()'))
    js = json.loads(jsblock)

    for j in js["markers"]:

        content = j.get("content")
        a = html.fromstring(content)
        slug = "".join(a.xpath("//a/@href"))

        page_url = f"{locator_domain}{slug}"
        phone = (
            "".join(a.xpath('//div[contains(text(), "Phone:")]/text()'))
            .replace("\n", "")
            .replace("Phone:", " ")
            .strip()
        )
        if phone.find(" ") != -1:
            phone = phone.split()[-1].strip()
        location_name = "".join(a.xpath("//h3/text()")).replace("\n", "").strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        if page_url == "https://www.daymarkrecovery.org/locations/fbc-iredell":
            page_url = "https://www.daymarkrecovery.org/locations"
        if page_url == "https://www.daymarkrecovery.org/locations/psr-chatham":
            page_url = "https://www.daymarkrecovery.org/locations"
        if page_url == "https://www.daymarkrecovery.org/locations/psr-person":
            page_url = "https://www.daymarkrecovery.org/locations"

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        r = session.get(page_url, headers=headers)

        tree = html.fromstring(r.text)

        location_type = "Daymark Recovery Services"

        ad = (
            " ".join(
                tree.xpath('//h3[text()="Contact"]/following-sibling::h4[1]/text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        f'//h3[./a[text()="{location_name}"]]/following-sibling::div/text()[position()<3]'
                    )
                )
                .replace("\n", "")
                .strip()
            ) or "<MISSING>"
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        '//h3[text()="Contact"]/following-sibling::strong/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        if street_address.find("815 Sanford Road") != -1:
            page_url = "https://www.daymarkrecovery.org/locations/psr-chatham-center"
        if street_address.find("211 Webb Street") != -1:
            page_url = "https://www.daymarkrecovery.org/locations/psr-person-center"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        if city.find("South Buies Creek") != -1:
            street_address = street_address + " " + city.split()[0].strip()
            city = " ".join(city.split()[1:])
        hours_of_operation = "<MISSING>"
        hours = (
            tree.xpath(
                '//h3[text()="Contact"]/following-sibling::p[./strong[contains(text(), "Hours")]][1]/strong/following-sibling::text()'
            )
            or "<MISSING>"
        )

        if hours != "<MISSING>":
            hours = list(filter(None, [a.strip() for a in hours]))
            hours_of_operation = " ".join(hours).replace(":", "").strip()
        hours_of_operation = (
            hours_of_operation.replace("Outpatient", "")
            .replace("BHUC Unit 24/7", "")
            .replace("After 5PM by Appt Only", "")
            .replace("  ", " ")
            .strip()
        )
        if hours_of_operation == "24/7":
            hours_of_operation = "24/7"
        if hours_of_operation != "24/7":
            hours_of_operation = (
                hours_of_operation.replace("24/7", "")
                .replace("730PM", "7:30PM")
                .strip()
            )
        if street_address.find("815 Sanford Road") != -1:
            hours_of_operation = "Mon-Fri 8AM to 5PM"

        if street_address.find("211 Webb Street") != -1:
            hours_of_operation = "Mon-Fri 8AM to 5PM"

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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
