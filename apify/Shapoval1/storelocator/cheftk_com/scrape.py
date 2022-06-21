import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.cheftk.com"
    urls = [
        "http://www.cheftk.com/tk-shabu-shabu-house-kona.html",
        "http://www.cheftk.com/tk-noodle-house-kona.html",
        "http://www.cheftk.com/lemongrass-express-waikoloa.html",
        "http://www.cheftk.com/gal-bi-808-bbq-mixed-plate.html",
        "http://www.cheftk.com/thep-thai-cuisine-.html",
    ]
    for i in urls:
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
        r = session.get(i, headers=headers)
        tree = html.fromstring(r.text)

        page_url = str(i)
        phone = (
            "".join(
                tree.xpath(
                    '//span[contains(text(), "(")]/text() | //strong[contains(text(), "(")]/text()'
                )
            )
            .replace("Phone", "")
            .replace(":", "")
            .replace("Call", "")
            .replace("(Nom Yen)", "")
            .strip()
        )
        phone = phone.replace("​    ", "").strip()
        phone = " ".join(phone.split())
        location_name = (
            "".join(
                tree.xpath(
                    '//div[@class="txt "]/div[1]//text() | //div[@class="txt "]/h6[1]//text()'
                )
            )
            .replace("   ", "")
            .strip()
            or "<MISSING>"
        )
        if page_url == "<MISSING>":
            location_name = "".join(tree.xpath('//div[@class="txt "]/p[1]//text()'))
        if page_url.find("808") != -1:
            location_name = "".join(
                tree.xpath(
                    '//div[@class="txt "]/p[1]//strong[@class="editor_color_green"]/text()'
                )
            )
        if page_url.find("thep-thai") != -1:
            location_name = "Thep Thai Cuisine"

        ad = "".join(tree.xpath('//div[@class="txt "]/div[2]//text()')) or "<MISSING>"
        if page_url.find("lemongrass-express-waikoloa.html") != -1:
            ad = (
                "".join(
                    tree.xpath(
                        '//div[@class="txt "]/h6[1]/following-sibling::p[1]//text()'
                    )
                )
                .replace("            ", "")
                .strip()
            )
        if page_url.find("808") != -1:
            ad = (
                "".join(
                    tree.xpath(
                        '//div[@class="txt "]/p[2]//strong[@class="editor_color_green"]/text()'
                    )
                )
                + " "
                + "".join(
                    tree.xpath(
                        '//div[@class="txt "]/p[3]//strong[@class="editor_color_green"]/text()'
                    )
                )
            )
        if page_url.find("thep-thai") != -1:
            ad = "".join(
                tree.xpath('//p/span//span[@style="font-size:20px;"]//text()')
            ).strip()
        if ad.find("Garlic") != -1:
            ad = ad.split("Garlic")[0].strip()
        ad = " ".join(ad.split())
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"
        if street_address.find("69-201") != -1:
            r = session.get("http://www.cheftk.com/contact-us.html", headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                "".join(
                    tree.xpath(
                        f'//div[./span[contains(text(), "{street_address}")]]/following-sibling::div[./span[contains(text(), "a.m.")]]//text()'
                    )
                )
                .replace(" ", "")
                .strip()
            )
            latitude = (
                "".join(
                    tree.xpath(f'//script[contains(text(), "{street_address}")]/text()')
                )
                .split("lat:")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(
                    tree.xpath(f'//script[contains(text(), "{street_address}")]/text()')
                )
                .split("lng:")[1]
                .split("}")[0]
                .strip()
            )
        if street_address.find("1103") != -1:
            r = session.get("http://www.cheftk.com/contact-us.html", headers=headers)
            tree = html.fromstring(r.text)
            slug = street_address.split()[0].strip()
            latitude = (
                "".join(tree.xpath(f'//script[contains(text(), "{slug}")]/text()'))
                .split("lat:")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath(f'//script[contains(text(), "{slug}")]/text()'))
                .split("lng:")[1]
                .split("}")[0]
                .strip()
            )
        if street_address.find("75-5722") != -1:
            hours_of_operation = "11:00 a.m. - 9:00 p.m. daily "

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
