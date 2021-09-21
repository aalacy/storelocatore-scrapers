import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://aspselfstorage.com"
    api_url = "https://aspselfstorage.com/locations"
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
    div = tree.xpath('//div[@class="facility_info"]/span')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        spage_url = f"https://aspselfstorage.com{slug}"

        session = SgRequests()
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)
        div_2 = tree.xpath('//div[@id="facilities"]/div[@class="data_source"]/a')
        for d in div_2:
            page_url = "".join(d.xpath(".//@href"))
            if page_url.find("http") == -1:
                page_url = f"https://aspselfstorage.com{page_url}"

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

            ad = " ".join(ad.split())
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
            city = a.get("city") or "<MISSING>"
            if street_address.find("Grand Junction") != -1:
                city = "Grand Junction"
                street_address = street_address.replace("Grand Junction", "").strip()
            if street_address.find("Fort") != -1:
                street_address = street_address.replace("Fort", "").strip()
                city = "Fort " + city
            latitude = (
                "".join(tree.xpath('//div[@id="single_map"]/@data-lat')) or "<MISSING>"
            )
            longitude = (
                "".join(tree.xpath('//div[@id="single_map"]/@data-lng')) or "<MISSING>"
            )
            phone = (
                "".join(tree.xpath('//div[@id="top_phone"]/a//text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(tree.xpath('//div[@id="top_office"]/text()'))
                .replace("\r\n", "")
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
