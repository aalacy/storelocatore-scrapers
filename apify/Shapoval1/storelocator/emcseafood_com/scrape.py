import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.emcseafood.com"
    api_url = "https://www.emcseafood.com/online-ordering/"
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
    div = tree.xpath('//a[contains(@class, "wp-block-button__link")]')
    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("topanga") != -1:
            page_url = "https://www.emcseafood.com/topanga/"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = " ".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
        adr = " ".join(tree.xpath("//a[contains(@href, 'google')]/text()"))
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
            .replace("tel:", "")
            .strip()
        )

        ad = adr.split("tel:")[0].strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        location_type = "Seafood Restaurant"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        city = a.get("city")
        ll = "".join(tree.xpath("//div/@data-markers")).replace("\\", "")
        latitude = ll.split('"lat":')[1].split(",")[0].strip()
        longitude = ll.split('"lng":')[1].split("}")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//table[@class="open_overview_widget-schedule"]//tr/td//text()'
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
