import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://prettykittywax.com/"
    api_url = "https://prettykittywax.com/"

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
    div = tree.xpath('//a[@style="color: #2d2d2d;"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if (
            page_url
            == "https://prettykittywax.wpengine.com/locations/tx/houston-wash-heights/"
        ):
            continue

        if page_url == "https://prettykittywax.com/locations/tx/houston-wash-heights/":
            continue
        if page_url == "https://prettykittywax.com/locations/tx/dallas-southlake/":
            page_url = "https://prettykittywax.com/locations/tx/dallas-south-lake/"

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = tree.xpath(
            '//div[@class="elementor-section-wrap"]/section[4]/div/div/div[1]//h2/text()'
        )
        ad = list(filter(None, [a.strip() for a in ad]))
        if "closed permanently" in "".join(ad):
            continue

        ad = " ".join(ad).replace("\n", " ").replace(",", "").strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        location_name = tree.xpath('//h2[contains(text(), "The Pretty Kitty")]/text()')
        try:
            location_name = "".join(location_name[0]).strip()
        except:
            location_name = "<MISSING>"

        location_type = "Location"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        if page_url == "https://prettykittywax.com/locations/tx/fort-worth-west-7th/":
            street_address = (
                "".join(
                    tree.xpath(
                        '//div[@class="elementor-section-wrap"]/section[4]/div/div/div[1]//h2/text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            city = (
                "".join(
                    tree.xpath(
                        '//div[@class="elementor-section-wrap"]/section[4]/div/div/div[1]//h2/text()[2]'
                    )
                )
                .replace("\n", "")
                .split(",")[0]
                .strip()
            )
        phone = "".join(
            tree.xpath(
                '//div[@class="elementor-section-wrap"]/section[4]/div/div/div[2]//a/text()'
            )
        ).strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="elementor-section-wrap"]/section[4]/div/div/div[3]//h2/text()'
                )
            )
            .replace("\n", "")
            .replace("   ", "  ")
            .strip()
        )
        if hours_of_operation.find("Modified Hours") != -1:
            hours_of_operation = "<MISSING>"
        cms = "".join(tree.xpath('//h2[contains(text(), "Coming Soon")]/text()'))
        if cms:
            continue

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
