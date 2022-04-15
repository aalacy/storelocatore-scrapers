import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://momsorganicmarket.com/"

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    page_urls = tree.xpath(
        '//ul[@id="top-menu"]/li[1]/ul[1]/li[position() > 1]/a/@href'
    )
    for i in page_urls:

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

        subr = session.get(i)
        trees = html.fromstring(subr.text)
        block = trees.xpath('//div[@class="et_pb_blurb_container"]')
        for b in block:
            ad = "".join(b.xpath(".//h1/following-sibling::div[1]/p[2]/text()"))

            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()

            city = a.get("city")

            state = a.get("state")
            postal = a.get("postal")
            country_code = "US"

            page_url = "".join(b.xpath(".//h1/a/@href")) or i
            cms = "".join(b.xpath('.//strong[contains(text(), "Coming Early")]/text()'))

            location_name = "".join(b.xpath(".//h1//text()"))
            phone = "".join(b.xpath(".//a[contains(@href, 'tel')]/text()"))

            hours_of_operation = b.xpath(
                ".//a[contains(@href, 'tel')]/following::p[1]//text()"
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation).replace(",", "")
            if street_address.find("83 Stanley Ave") != -1:
                phone = "".join(
                    b.xpath(".//div[@class='et_pb_blurb_description']/p[3]/text()")
                )
                hours_of_operation = b.xpath(
                    ".//div[@class='et_pb_blurb_description']/p[5]//text()"
                )
                hours_of_operation = list(
                    filter(None, [a.strip() for a in hours_of_operation])
                )
                hours_of_operation = " ".join(hours_of_operation).replace(",", "")

            hours_of_operation = hours_of_operation.replace("\n", " ").strip()
            rr = session.get(page_url)
            ttree = html.fromstring(rr.text)
            text = "".join(ttree.xpath(".//a[1][contains(@href, 'google')]/@href"))
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"
            if latitude == "<MISSING>":
                text = "".join(ttree.xpath("//div/@data-et-multi-view"))
                try:
                    if text.find("ll=") != -1:
                        latitude = text.split("ll=")[1].split(",")[0]
                        longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                    else:
                        latitude = text.split("@")[1].split(",")[0]
                        longitude = text.split("@")[1].split(",")[1]
                except IndexError:
                    latitude, longitude = "<MISSING>", "<MISSING>"
            if cms:
                phone, hours_of_operation = "<MISSING>", "Coming Soon"
            if hours_of_operation.find("Hour") != -1:
                hours_of_operation = hours_of_operation.split("Hour")[1].strip()

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
    locator_domain = "https://momsorganicmarket.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
