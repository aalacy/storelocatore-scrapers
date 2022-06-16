import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.yoursterlingpharmacy.com"
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

    r = session.get("https://www.yoursterlingpharmacy.com/locations", headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="location-directory-hours"]/a[contains(@href, "/pharmacy")]'
    )
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(d.xpath(".//preceding::h2[1]/strong/text()"))
        phone = "".join(d.xpath('.//preceding::a[contains(@href, "tel")][1]/text()'))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = "".join(tree.xpath('//a[text()="Directions"]/@href')) or "<MISSING>"

        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        if ad != "<MISSING>":
            ad = (
                ad.split("q=")[1]
                .split("+U.S.")[0]
                .replace("%2C", "")
                .replace("+", " ")
                .strip()
            )
            ad = ad.replace("Le Sueur MN 56058 Le Sueur MN 56058", "Le Sueur MN 56058")
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            city = a.get("city") or "<MISSING>"
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
        if city.find("St") != -1:
            street_address = street_address + " St"
            city = city.replace("St", "").strip()
        location_type = "pharmacy"
        hours_of_operation = (
            " ".join(
                tree.xpath('//ol[@class="location-header-info__hours-list"]/li//text()')
            )
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            session = SgRequests()
            r = session.get(
                "https://rhshc.com/services/cresco-family-pharmacy/", headers=headers
            )
            tree = html.fromstring(r.text)

            street_address = (
                "".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Cresco Family")]]/following-sibling::p[1]/text()[1]'
                    )
                )
                or "<MISSING>"
            )
            adr = (
                "".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Cresco Family")]]/following-sibling::p[1]/text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            city = adr.split(",")[0].strip() or "<MISSING>"
            state = adr.split(",")[1].split()[0].strip() or "<MISSING>"
            postal = adr.split(",")[1].split()[1].strip() or "<MISSING>"
            phone = (
                "".join(
                    tree.xpath('//div[@class="location-header-info__phone"]/a/text()')
                )
                or "<MISSING>"
            )

            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Cresco Family")]]/following-sibling::p[2]/text()'
                    )
                )
                .replace("\n", "")
                .replace("HOURS:", "")
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
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
