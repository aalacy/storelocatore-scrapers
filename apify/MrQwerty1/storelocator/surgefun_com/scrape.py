import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    locator_domain = "https://surgefun.com"
    api_url = "https://surgefun.com/locations/"
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
    div = tree.xpath('//a[.//span[text()="LEARN MORE"]]')
    for d in div:
        page_url = "".join(d.xpath(".//@href")) + "contactus/"
        if page_url == "https://surgefun.com/locations/bossier-city/contactus/":
            page_url = "https://surgefun.com/locations/bossier-city"
        location_name = "".join(d.xpath(".//preceding::h2[2]/text()"))

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath(
                    "//div[./div/h2[contains(text(), 'CONTACT')]]/following-sibling::div[1]//text()"
                )
            )
            .replace("\n", "")
            .replace("\\xa0", "")
            .strip()
        )
        if tree.xpath("//h2[contains(text(), 'COMING SOON')]"):
            continue

        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        phone = "".join(
            tree.xpath("//span[contains(text(), 'Phone')]/following-sibling::a/text()")
        ).strip()
        if not phone:
            phone = "".join(
                tree.xpath(
                    "//div[./div/h2[contains(text(), 'PHONE')]]/following-sibling::div[1]//text()"
                )
            ).strip()

        try:
            ids = (
                "".join(tree.xpath('//script[contains(text(), "const loc=")]/text()'))
                .split("const loc=")[1]
                .split(";")[0]
                .strip()
            )
            r = session.get(f"https://plondex.com/wp/jsonquery/loadloc/9/{ids}")
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(
                    tree.xpath('//div[./*[contains(text(), "Business Hours")]]//text()')
                )
                .replace("Business Hours", "")
                .replace("\n", "")
                .strip()
            )
        except:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    with SgRequests() as session:
        with SgWriter(
            SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
        ) as writer:
            fetch_data(writer)
