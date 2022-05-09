import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://holtzmancorp.com/holtzman-propane-locations/"

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//section[@id="siteorigin-panels-builder-2"]/div/div[.//p[contains(text(), "(")]]//div[@class="siteorigin-widget-tinymce textwidget"]'
    )
    for d in div:

        info = " ".join(d.xpath(".//*//text()")).replace("\n", "").strip()
        info = (
            " ".join(info.split())
            .replace("( 540)", "(540)")
            .replace(" - ", " ")
            .replace(" -", "-")
        )
        if not info[0].isdigit():
            continue
        adr = " ".join(info.split()[:-2]).replace("Mt.", "Mount")
        a = usaddress.tag(adr, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        slug_street = street_address.split()[0].strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"

        location_type = (
            "".join(d.xpath(".//preceding::h5[1]/strong/span[1]/text()"))
            .replace("For", "")
            .replace("inquiries", "")
            .strip()
            .capitalize()
        )
        location_name = f"Holtzman Corp {location_type}" + " " + city.capitalize()
        page_url = (
            "".join(
                d.xpath(
                    f'.//preceding::div/p[contains(text(), "{slug_street}")]/preceding-sibling::p/a/@href'
                )
            )
            or "https://holtzmancorp.com/holtzman-propane-locations/"
        )

        map_link = "".join(
            d.xpath(
                f'.//preceding::div/p[contains(text(), "{slug_street}")]/following-sibling::p/iframe/@src'
            )
        )
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = " ".join(info.split()[-2:])

        hours_of_operation = "<MISSING>"
        cms = "".join(d.xpath('.//span[contains(text(),"Coming Soon")]/text()'))
        if phone == "Coming Soon!":
            phone = "<MISSING>"
            hours_of_operation = "Coming Soon"
        if cms:
            hours_of_operation = "Coming Soon"
        if page_url != "https://holtzmancorp.com/holtzman-propane-locations/":
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Hours")]]/following-sibling::p[1]//text()'
                    )
                )
                .replace("\n", "")
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://holtzmancorp.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
