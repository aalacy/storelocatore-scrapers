import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://aspselfstorage.com"
    api_url = "https://aspselfstorage.com/sitemap.xml"
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
    tree = html.fromstring(r.content)
    div = tree.xpath('//url/loc[contains(text(), "self-storage")]')
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        if (
            page_url
            == "https://www.aspselfstorage.com/self-storage/Colorado-Springs-CO-80920"
        ):
            page_url = "https://www.securcareselfstorage.com/storage/colorado/storage-units-colorado-springs/1825-Jamboree-Dr-1069"
        if (
            page_url
            == "https://www.aspselfstorage.com/self-storage/spring-valley-ca-919786"
        ):
            page_url = "https://securespace.com/storage-units/ca/spring-valley-self-storage/11902-campo-rd-spring-valley-ca-91978"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//div[@id="top_right"]/h2/text()')) or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = (
                "".join(tree.xpath("//h1//text()")).replace("\n", "").strip()
                or "<MISSING>"
            )
        ad = (
            "".join(tree.xpath('//div[@id="top_address"]//a//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        '//h1/following::div[1]//p[@class="facility-address"]/text() | //a[@id="facility-address"]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        ad = " ".join(ad.split())
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()

        city = a.get("city")
        if street_address.find("Grand Junction") != -1:
            city = "Grand Junction"
            street_address = street_address.replace("Grand Junction", "").strip()
        if street_address.find("Fort") != -1:
            street_address = street_address.replace("Fort", "").strip()
            city = "Fort " + city
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        latitude = (
            "".join(tree.xpath('//div[@id="single_map"]/@data-lat')) or "<MISSING>"
        )
        longitude = (
            "".join(tree.xpath('//div[@id="single_map"]/@data-lng')) or "<MISSING>"
        )
        text = "".join(
            tree.xpath(
                '//div[@class="review-source"]/a/@href | //a[contains(@href, "https://www.google.com/maps/dir")]/@href'
            )
        )
        if latitude == "<MISSING>":
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(tree.xpath('//div[@id="top_phone"]/a//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    tree.xpath(
                        '//h1/following::div[1]//a[contains(@href, "tel")]/text() | //div[@class="ss-facility-phone"]//a/text()'
                    )
                )
                or "<MISSING>"
            )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@id="top_office"]/text()'))
            .replace("\r\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[@id="facility-hours"]//div[@class="office-hours-wrapping-header"]/following-sibling::table[1]//tr/td//text() | //div[@class="ss-facility-phone"]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", "")
                .replace("Office Hours:", "")
                .strip()
                or "<MISSING>"
            )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

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
