from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, post=""):
    if post:
        adr = parse_address(International_Parser(), line, postcode=post)
    else:
        adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street_address, city, postal


def get_coords():
    coords = dict()
    api = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/11232/stores.js"
    r = session.get(api)
    js = r.json()["stores"]

    for j in js:
        phone = j.get("phone") or ""
        key = phone.replace(" ", "")[-8:]
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        coords[key] = (latitude, longitude)

    return coords


def fetch_data(sgw: SgWriter):
    coords = get_coords()
    page_url = "https://www.frenchconnection.com/pages/store-locator"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='store']")
    for d in divs:
        text = "".join(d.xpath("./@data-address")).upper()
        source = "".join(d.xpath("./@data-opening"))
        root = html.fromstring(text)
        lines = root.xpath("//text()")
        phone = lines.pop()
        postal = SgRecord.MISSING
        if phone[0].isalpha():
            postal = phone.split("0")[0]
            phone = phone.replace(postal, "")
        phone = phone.replace("(", "").replace(")", "").replace(" ", "").lower()
        if "ext" in phone:
            phone = phone.split("ext")[0]
        key = phone[-8:]
        latitude, longitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)

        brands = ["HOUSE OF FRASER", "FENWICK", "JOHN LEWIS", "FRENCH CONNECTION"]
        i = 0
        for line in lines:
            for b in brands:
                if b in line:
                    break
            else:
                i += 1
                continue
            break

        if i == len(lines):
            i = 0
        if lines[i + 1] in lines[i]:
            i += 1

        location_name = lines[i]
        raw_address = ", ".join(lines[i + 1 :]).replace(",,", ",")
        country = "UK"
        if "IRELAND" in raw_address:
            country = "IE"
            raw_address = raw_address.replace(", IRELAND", "")
        if "AMSTERDAM" in raw_address:
            country = "NL"

        location_type = "Retail"
        if "outlet" in location_name.lower():
            location_type = "Outlet"
        street_address, city, postal = get_international(raw_address, postal)
        if (
            (postal == SgRecord.MISSING and country == "UK")
            or len(postal) < 2
            or len(postal) > 10
        ):
            postal = raw_address.split(", ")[-1]
        if len(street_address) < 3 or ("5A" in postal and "5A" in street_address):
            street_address = raw_address.split(", ")[0]
        if city == SgRecord.MISSING and country == "UK":
            city = raw_address.split(", ")[-2]
        if city == SgRecord.MISSING and country == "IE":
            city = raw_address.split(", ")[0]
        if city.upper() in street_address.upper():
            street_address = street_address.upper().replace(city.upper(), "", 1)
        if postal.upper() in street_address.upper():
            street_address = street_address.upper().replace(postal.upper(), "")

        try:
            hours_of_operation = (
                html.fromstring(source).xpath(".//text()")[-2].replace(":00 ", ":00;")
            )
        except:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.frenchconnection.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
