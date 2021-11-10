import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kadlec.org"
    api_url = "https://www.kadlec.org/location-directory"
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
        '//option[text()="Select a location type"]/following-sibling::option'
    )
    for d in div:
        slug = "".join(d.xpath(".//@value"))
        location_type = "".join(d.xpath(".//text()"))
        for i in range(1, 10):
            loc_type_page = f"https://www.kadlec.org/location-directory/search-results?type={slug}&page={i}"

            session = SgRequests()
            r = session.get(loc_type_page, headers=headers)
            tree = html.fromstring(r.text)
            div = tree.xpath('//li[@class="col-sm-12"]')

            for d in div:

                page_url = f"https://www.kadlec.org{''.join(d.xpath('.//h4/a/@href'))}"
                if page_url.find("express-care") != -1:
                    page_url = f"https://kadlec.azureedge.net/our-services/urgent-care/{''.join(d.xpath('.//h4/a/@href')).split('/')[-1].split('-')[0]}-{''.join(d.xpath('.//h4/a/@href')).split('-')[-1]}".replace(
                        "express", "expresscare"
                    )
                if (
                    page_url.find(
                        "https://www.kadlec.org/location-directory/u/urgent-care-kennewick"
                    )
                    != -1
                ):
                    page_url = "https://kadlec.azureedge.net/our-services/urgent-care/urgent-care-kennewick"
                page_url = page_url.replace(
                    "expresscare-lakes", "expresscare-canyon-lakes"
                )

                location_name = (
                    "".join(d.xpath(".//h4/a/text()")).replace("\n", "").strip()
                )
                ad = (
                    " ".join(d.xpath(".//h4/following-sibling::div[1]/text()"))
                    .replace("\r\n", "")
                    .strip()
                )
                ad = " ".join(ad.split())
                a = usaddress.tag(ad, tag_mapping=tag)[0]
                street_address = (
                    "".join(d.xpath(".//h4/following-sibling::div[1]/text()[1]"))
                    .replace("\n", "")
                    .strip()
                )
                if (
                    street_address == "888 Swift Boulevard"
                    and location_type == "Hospital"
                ):
                    street_address = "888 Swift Blvd"
                if (
                    street_address == "1100 Goethals Drive, Suite E"
                    and location_name == "Kadlec Clinic - Cardiothoracic Surgery"
                ):
                    street_address = "1100 Goethals Dr., Suite E"
                if (
                    street_address == "3001 St. Anthony Way, Suite 115"
                    and page_url
                    == "https://www.kadlec.org/location-directory/i/inland-cardiology-pendleton"
                ):
                    street_address = "3001 Street Anthony Way, Suite 115"
                state = a.get("state")
                postal = a.get("postal") or "<MISSING>"
                country_code = "US"
                city = a.get("city")
                phone = (
                    "".join(
                        d.xpath(
                            './/div[@class="locations-listing-phones"]/div[1]/a/text()'
                        )
                    )
                    or "<MISSING>"
                )
                session = SgRequests()
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//div[@class="hours-text text-muted wm_hours"]//text() | //span[@class="glyphicon glyphicon-time location-contactus-item-media"]/following-sibling::div//text()'
                        )
                    )
                    .replace("\r\n", "")
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                if hours_of_operation.find("Phone") != -1:
                    hours_of_operation = hours_of_operation.split("Phone")[0].strip()
                if hours_of_operation.find("X-Ray") != -1:
                    hours_of_operation = hours_of_operation.split("X-Ray")[0].strip()
                if (
                    page_url.find(
                        "https://www.kadlec.org/location-directory/n/northwest-orthopaedic-and-sports-medicine"
                    )
                    != -1
                ):
                    hours_of_operation = "Monday-Friday 8 a.m.-5 p.m."
                if hours_of_operation == "By appointment":
                    hours_of_operation = "<MISSING>"
                hours_of_operation = (
                    hours_of_operation.replace("&nbsp&nbsp", "")
                    .replace("  ", " ")
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
