import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.nightlitepediatrics.com/"
    api_url = "https://www.nightlitepediatrics.com/locations-pediatrics-urgent-care-in-florida"
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
    div = tree.xpath(
        '//div[@class="wp-block-columns alignwide locationstext1 has-white-color has-text-color has-background"]/div[1]/h2[1]/a'
    )
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        try:
            phone = (
                "".join(d.xpath(".//following::h2[1]/a/text()"))
                .split("Phone:")[1]
                .strip()
            )
        except:
            phone = "<MISSING>"
        phone_url = "".join(
            d.xpath(
                './/following::div[@class="wp-block-column pg-col-03-loc"][1]//h2/a/@href'
            )
        )
        if phone_url.find("http") == -1:
            phone_url = f"https://www.nightlitepediatrics.com{phone_url}"

        if page_url.find("telemedicine") != -1:
            continue

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath(
                    '//strong[text()="Get Google Maps Directions to"]/following-sibling::text()'
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
        location_name = (
            "".join(
                tree.xpath(
                    '//h2[./a[contains(@href, "maps")]]/preceding-sibling::h1/text()'
                )
            )
            .replace("Directions to", "")
            .strip()
        )
        country_code = "US"
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

        hours_of_operation = (
            " ".join(tree.xpath('//strong[text()="Hours:"]/following-sibling::text()'))
            .replace("\n", "")
            .replace("Open", "")
            .strip()
        )
        if phone == "<MISSING>":
            session = SgRequests()
            r = session.get(phone_url, headers=headers)
            tree = html.fromstring(r.text)
            phone = (
                "".join(tree.xpath('//a[contains(text(), "New Patients:")]/text()'))
                .replace("New Patients:", "")
                .strip()
                or "<MISSING>"
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
