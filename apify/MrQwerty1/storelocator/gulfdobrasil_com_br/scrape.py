from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_city(line):
    adr = parse_address(International_Parser(), line)
    city = adr.city or SgRecord.MISSING
    return city


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "http://www.gulfdobrasil.com.br/wp-admin/admin-ajax.php?action=loadGlobalContacts"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        g = j.get("geolocation") or {}
        location_name = j.get("title")
        source = j.get("address") or "<html>"
        tree = html.fromstring(source)
        raw_address = " ".join(" ".join(tree.xpath("//text()")).split())
        street_address = g.get("name")
        if street_address:
            city = get_city(raw_address)
            state = g.get("state_short")
            postal = g.get("post_code") or ""
        else:
            street_address, city, state, postal = get_international(raw_address)

        postal = postal.replace("CEP", "").strip()
        country_code = j.get("country")
        phone = j.get("phone") or ""
        if "/" in phone:
            phone = phone.split("/")[0].strip()
        if phone.count("("):
            phone = phone.split("(")[-1].replace(")", "")
        latitude = g.get("lat")
        longitude = g.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.gulfdobrasil.com.br/"
    page_url = "http://www.gulfdobrasil.com.br/onde-encontrar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
