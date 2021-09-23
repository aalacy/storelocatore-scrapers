import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://clubchampiongolf.com"
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
    data = {
        "searchname": "",
        "filter_catid": "",
        "searchzip": "Please enter your zip code (i.e. 60527)",
        "task": "search",
        "qradius": "9",
        "radius": "-1",
        "option": "com_mymaplocations",
        "limit": "0",
        "component": "com_mymaplocations",
        "Itemid": "102",
        "zoom": "10",
        "format": "json",
        "geo": "",
        "latitude": "",
        "longitude": "",
        "limitstart": "0",
    }

    r = session.post(
        "https://clubchampiongolf.com/locations", headers=headers, data=data
    )
    js = r.json()["features"]
    for j in js:

        slug = "".join(j.get("properties").get("url")).replace(".", "").strip()
        page_url = f"https://clubchampiongolf.com{slug}"
        location_name = j.get("properties").get("name")
        store_number = j.get("id")
        latitude = j.get("geometry").get("coordinates")[1]
        longitude = j.get("geometry").get("coordinates")[0]

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath(
                    '//tr[.//a[contains(@href, "tel")]]/following-sibling::tr//span//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if ad.find("(") != -1:
            ad = ad.split("(")[0].strip()

        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        phone = "".join(
            tree.xpath('//tbody//td[2]//a[contains(@href, "tel")]/text()')
        ).strip()
        hours_of_operation = " ".join(
            tree.xpath("//div[./h3]/following-sibling::div[1]//text()")
        )
        if hours_of_operation.find("GET") != -1:
            hours_of_operation = hours_of_operation.split("GET")[0].strip()
        if hours_of_operation.find("Get") != -1:
            hours_of_operation = hours_of_operation.split("Get")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
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
