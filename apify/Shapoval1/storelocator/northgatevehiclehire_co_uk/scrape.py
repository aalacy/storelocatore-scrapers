from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.northgatevehiclehire.co.uk/"
    api_url = "https://nvh-v2-api.azurewebsites.net/api/branches?locationName=&isHireCentre=true&isWorkshop=true&num=999"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["results"]
    for j in js:
        slug = j.get("url")
        page_url = f"https://www.northgatevehiclehire.co.uk{slug}"
        location_name = j.get("name")
        ad = j.get("address")
        b = html.fromstring(ad)
        adr = " ".join(b.xpath("//*//text()")).replace("\n", "").strip()
        adr = " ".join(adr.split())
        postal = j.get("postcode")
        a = parse_address(International_Parser(), adr)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "")
            .replace("Bl6 4Bl", "")
            .strip()
        )
        state = j.get("area") or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = location_name
        loc_tmp = []
        isWorkshop = j.get("isWorkshop")
        isHireCentre = j.get("isHireCentre")
        if isWorkshop:
            loc_tmp.append("Workshop")
        if isHireCentre:
            loc_tmp.append("HireCentre")
        location_type = ", ".join(loc_tmp)
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = "".join(j.get("telephone").get("title")).strip()
        if phone.find("<") != -1:
            phone = phone.split(">")[1].split("<")[0].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[text()="Opening Hours"]/following-sibling::ul/li/p/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
