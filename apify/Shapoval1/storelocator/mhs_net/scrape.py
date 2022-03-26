import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://www.mhs.net/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@name="city"]/option[position()>1]')

    for d in div:
        slug = "".join(d.xpath(".//@value"))
        slCity = slug.split(",")[0].strip()
        slState = slug.split(",")[1].strip()
        session = SgRequests()
        for i in range(1, 3):
            params = (
                ("city", f"{slCity}, {slState}"),
                ("pg", f"{i}"),
            )
            r = session.get(
                "https://www.mhs.net/locations/search-results",
                headers=headers,
                params=params,
            )

            tree = html.fromstring(r.text)

            block = tree.xpath('//a[contains(text(), "Read More")]')
            for b in block:

                page_url = "https://www.mhs.net" + "".join(b.xpath(".//@href"))
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
                }
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)

                location_name = (
                    "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
                )

                ad = (
                    " ".join(tree.xpath('//div[@class="module-lc-address"]/div/text()'))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                if ad == "<MISSING>":
                    ad = (
                        " ".join(tree.xpath('//div[@class="info"]/text()'))
                        .replace("•", "")
                        .strip()
                    )
                ad = (
                    ad.replace("Memorial Primary Care", "")
                    .replace("Outpatient Pharmacy", "")
                    .replace("Memorial Healthcare System", "")
                    .replace("Memorial Regional Hospital", "")
                    .replace("Medical Office Building", "")
                )
                ad = (
                    ad.replace("Hollywood Beach Cultural and Community Center", "")
                    .replace("Boulevard Heights Community Center", "")
                    .replace("Memorial Hospital Miramar", "")
                    .replace("Memorial Hospital West", "")
                )
                ad = ad.strip()
                a = usaddress.tag(ad, tag_mapping=tag)[0]

                street_address = (
                    f"{a.get('address1')} {a.get('address2')}".replace("None", "")
                    .replace("954-987-2000", "")
                    .strip()
                    or "<MISSING>"
                )

                phone = (
                    "".join(tree.xpath('//div[contains(text(), "Phone:")]/text()'))
                    .replace("\r\n", "")
                    .replace("Phone:", "")
                    .strip()
                    or "<MISSING>"
                )
                if phone.find("A") != -1:
                    phone = phone.split("A")[0].strip()
                if phone == "<MISSING>":
                    phone = (
                        "".join(
                            tree.xpath('//a[contains(@href, "tel")]/text()')
                        ).replace("Telehealth Services", "")
                        or "<MISSING>"
                    )
                phone = phone or "<MISSING>"
                state = a.get("state") or "<MISSING>"
                postal = a.get("ZipCode") or "<MISSING>"
                country_code = "US"
                city = a.get("city") or "<MISSING>"
                if city.find("Lobby") != -1:
                    city = city.replace("Lobby", "").strip()
                    street_address = street_address + " " + "Lobby"

                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//h2[contains(text(), "Hours")]/following-sibling::div//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                if hours_of_operation.find("Email") != -1:
                    hours_of_operation = hours_of_operation.split("Email")[0].strip()
                if hours_of_operation.find("Pharmacy") != -1:
                    hours_of_operation = hours_of_operation.split("Pharmacy")[0].strip()
                if hours_of_operation.find("Psychiatric medication clinic:") != -1:
                    hours_of_operation = (
                        hours_of_operation.split("Psychiatric medication clinic:")[1]
                        .split("Counseling")[0]
                        .strip()
                    )
                if hours_of_operation.find("Valet") != -1:
                    hours_of_operation = hours_of_operation.split("Valet")[0].strip()
                try:
                    if hours_of_operation.find("Laboratory Hours") != -1:
                        hours_of_operation = (
                            hours_of_operation.split("Laboratory Hours")[1]
                            .split("Outpatient")[0]
                            .strip()
                        )
                except:
                    if hours_of_operation.find("Laboratory Hours") != -1:
                        hours_of_operation = hours_of_operation.split(
                            "Laboratory Hours"
                        )[1].strip()
                if hours_of_operation.find("Due to COVID-19") != -1:
                    hours_of_operation = hours_of_operation.split("Due to COVID-19")[
                        0
                    ].strip()
                if hours_of_operation.find("TBD") != -1:
                    hours_of_operation = "Coming Soon"
                hours_of_operation = (
                    hours_of_operation.replace(
                        " Holiday hours vary, call for times", ""
                    )
                    .replace("Office Hours", "")
                    .replace("Clinic Hours", "")
                    .replace("On-call is available 24/7", "")
                    .replace(" (Rehabilitation's last appointment)", "")
                    .strip()
                )
                if street_address.find("1951") != -1:
                    hours_of_operation = (
                        " ".join(
                            tree.xpath(
                                '//h2[contains(text(), "Hours")]/following-sibling::div//text()'
                            )
                        )
                        .replace("\n", "")
                        .replace("Outpatient Pharmacy Hours", "")
                        .strip()
                    )
                if hours_of_operation.find("Email") != -1:
                    hours_of_operation = hours_of_operation.split("Email")[0].strip()
                if hours_of_operation.find("Varies") != -1:
                    hours_of_operation = "<MISSING>"
                if hours_of_operation.find("Phone:") != -1:
                    hours_of_operation = hours_of_operation.split("Phone:")[0].strip()

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
                    latitude=SgRecord.MISSING,
                    longitude=SgRecord.MISSING,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.mhs.net"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
