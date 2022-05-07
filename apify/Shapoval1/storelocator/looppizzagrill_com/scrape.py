import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://www.powr.io/wix/map/public.json?pageId=rrcup&compId=comp-kiespl6j3&viewerCompId=comp-kiespl6j3&siteRevision=753&viewMode=site&deviceType=desktop&locale=en&tz=America%2FNew_York&width=455&height=544&instance=Lfl7ze0je2ZLRYoU5k7QLSjcH9Fe2VpDPMQCszgrUmg.eyJpbnN0YW5jZUlkIjoiMDA3ZGU4OWUtNjdjNC00ZWM5LWEwMDktYzdkMjI5YzA1YjEyIiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMjEtMDMtMDdUMTE6Mjg6MDEuMzkwWiIsInZlbmRvclByb2R1Y3RJZCI6ImJ1c2luZXNzIiwiZGVtb01vZGUiOmZhbHNlLCJhaWQiOiI0NjM5N2Q5ZC1lMTYzLTRjNzMtYWIzOS05MTA3YTc2MjAxZjQiLCJzaXRlT3duZXJJZCI6ImZkMjE4YmNjLTU5NjUtNGVkNC1hY2E5LTdkYjRiNWUzOTQxMSJ9&currency=USD&currentCurrency=USD&vsi=67acc5b7-0def-4cc0-b3e8-6a1704fbf80b&commonConfig=%7B%22brand%22%3A%22wix%22%2C%22bsi%22%3A%22cb096e66-5b78-40af-9913-b2c7f9d2b707%7C3%22%2C%22BSI%22%3A%22cb096e66-5b78-40af-9913-b2c7f9d2b707%7C3%22%7D&url=https://www.thelooprestaurant.com/durham-nc"
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

    r = session.get(api_url)
    js = r.json()

    for j in js["content"]["locations"]:

        ad = "".join(j.get("address"))
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        slug = street_address.split()[0].strip()
        city = a.get("city")
        postal = a.get("postal")
        state = a.get("state")
        country_code = a.get("CountryName")
        location_name = f"{j.get('name').replace('<p>', '').replace('</p>', '')} - {j.get('description').replace('<p>', '').replace('</p>', '')}"
        loc_slug = location_name.split("-")[1].split()[0].strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        r = session.get("https://www.thelooprestaurant.com/locations")
        tree = html.fromstring(r.text)

        info_block = tree.xpath(f'//span[contains(text(), "{slug}")]//a//text()')
        info_block = list(filter(None, [b.strip() for b in info_block]))
        if not info_block:
            info_block = tree.xpath(
                f'//span[contains(text(), "{slug}")]/following::a[1]//text()'
            )
            info_block = list(filter(None, [b.strip() for b in info_block]))
        if not info_block:
            info_block = tree.xpath(
                f'//span[contains(text(), "{loc_slug} ")]/following::a[1]//text()'
            )
            info_block = list(filter(None, [b.strip() for b in info_block]))
        phone = "".join(info_block) or "<MISSING>"
        hours_of_operation = (
            "".join(
                tree.xpath('//span[contains(text(), "Hours of Operation:")]/text()')
            )
            .replace("Hours of Operation:", "")
            .strip()
        )
        page_url = (
            "".join(
                tree.xpath(
                    f'//*[contains(text(), "{phone}")]/following::a[.//span[text()="link to page"]][1]/@href'
                )
            )
            or "https://www.thelooprestaurant.com/locations"
        )
        r = session.get(page_url)
        if r.status_code == 404:
            page_url = "https://www.thelooprestaurant.com/locations"

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
    locator_domain = "https://www.thelooprestaurant.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
