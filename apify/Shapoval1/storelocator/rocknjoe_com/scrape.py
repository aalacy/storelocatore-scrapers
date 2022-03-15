import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.rocknjoe.com"
    page_url = "https://www.rocknjoe.com/locations"
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
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./h6//span[text()="Hours"]]')

    for d in div:

        location_type = "Rock 'n' Joe Coffee"
        adr = d.xpath(
            './/preceding-sibling::div[./p[@style="line-height:1.7em; font-size:17px;"]][1]//text()'
        )
        adress = " ".join(adr[:-1]).replace("\n", "").strip()
        if "404" in adress:
            adress = " ".join(adr).replace("\n", "").strip()
        if "".join(adr).find("Clinic") != -1:
            adress = " ".join(adr).replace("\n", "").strip()
        a = usaddress.tag(adress, tag_mapping=tag)[0]
        phone = "".join(adr[-1])
        if "".join(adr).find("420") != -1:
            phone = "<MISSING>"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()

        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        location_name = (
            "".join(d.xpath(".//preceding-sibling::div[5]/h6//text()")) or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = "".join(d.xpath(".//preceding-sibling::div[3]/h6//text()"))
        if street_address.find("404 Wood Street") != -1:
            location_name = "".join(
                d.xpath(
                    './/preceding-sibling::div[./h6[@style="font-size:22px;"]][1]//text()'
                )
            )
        days = d.xpath(
            ".//following-sibling::div[./p[@style='line-height:1.7em; font-size:17px;']][1]//text()"
        )
        days = list(filter(None, [a.strip() for a in days]))

        times = (
            d.xpath(
                ".//following-sibling::div[./p[@style='line-height:1.7em; font-size:17px;']][2]//text()"
            )
            or "<MISSING>"
        )
        if times != "<MISSING>":
            times = list(filter(None, [a.strip() for a in times]))
        if times == "<MISSING>":
            times = d.xpath(".//following::div[2]/p/span/text()")
        _tmp = []
        if days != "<MISSING>" and times != "<MISSING>":
            for b, t in zip(days, times):
                _tmp.append(f"{b.strip()}: {t.strip()}")
        hours_of_operation = " ".join(_tmp) or "<MISSING>"
        cms = "".join(
            d.xpath(
                './/following-sibling::div/p[./span[contains(text(), "Coming Soon")]]//text()'
            )
        )
        if cms and street_address.find("404") != -1:
            phone = "<MISSING>"
            hours_of_operation = "Coming Soon"

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
            raw_address=adress,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
