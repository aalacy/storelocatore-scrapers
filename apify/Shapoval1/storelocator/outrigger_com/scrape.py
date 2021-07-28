import usaddress
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.outrigger.com/hotels-resorts", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//a[contains(text(), "View Hotel >")]/@href')


def fetch_data(sgw: SgWriter):

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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.outrigger.com/hotels-resorts", headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "View Hotel >")]')
    for d in div:
        page_url = f"{locator_domain}{''.join(d.xpath('.//@href'))}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        }
        r = session.get(page_url, headers=headers)

        tree = html.fromstring(r.text)
        info = tree.xpath(
            '//a[contains(@href, "email")]/preceding-sibling::text() | //span[contains(text(), "78-128 Ehukai")]/text() | //span[contains(text(), "P.O. Box 173")]/text() | //span[contains(text(), "Castaway Island, Fiji")]/text() | //a[contains(@href, "email")]/preceding-sibling::*/text()'
        )

        info = list(filter(None, [a.strip() for a in info]))
        ad = " ".join(info[:2])
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "69-250 Waikoloa Beach Drive":
            street_address = street_address + " " + "".join(info[2]).strip()
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
        if location_name.find("Ocean ViewOcean") != -1:
            location_name = location_name.split("Ocean ViewOcean")[0].strip()
        if location_name == "<MISSING>":
            location_name = "".join(tree.xpath("//h2/text()")) or "<MISSING>"
        if location_name.find("Save over") != -1:
            location_name = location_name.split("Save over")[0].strip()
        if location_name.find("Castaway Island, Fiji") != -1:
            city = location_name.split(",")[0].strip()
            state = location_name.split(",")[1].strip()
        if location_name.find("OUTRIGGER MAURITIUS BEACH RESORT") != -1:
            city = "".join(info[1]).split(",")[0].strip()
            state = "".join(info[1]).split(",")[1].strip()

        phone = (
            "".join(tree.xpath('//span/a[contains(@href, "tel")][1]/text()')).strip()
            or "<MISSING>"
        )
        if "".join(info).find("T:") != -1:
            try:
                phone = (
                    "".join(info).split("T:")[1].split("|")[0].strip() or "<MISSING>"
                )
            except:
                phone = "<MISSING>"
        if "".join(info).find("Ph:") != -1:
            try:
                phone = (
                    "".join(info).split("Ph:")[1].split("Fax:")[0].strip()
                    or "<MISSING>"
                )
            except:
                phone = "<MISSING>"
        if phone.find("or") != -1:
            phone = phone.split("or")[0].strip()
        if phone.find("Reservations:") != -1:
            phone = phone.split("Reservations:")[0].strip()
        if "".join(info).find("Property Phone:") != -1:
            phone = "".join(info).split("Property Phone:")[1].split("Hawaii")[0].strip()
        phone = phone.replace("Toll-free", "").strip()

        hours_of_operation = "<MISSING>"
        cms = "".join(tree.xpath('//p[contains(text(), "Opening ")]/text()'))
        if cms:
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
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.outrigger.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
