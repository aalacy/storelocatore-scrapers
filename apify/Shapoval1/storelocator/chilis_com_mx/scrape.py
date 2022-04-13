import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.chilis.com.mx/"
    api_url = "https://www.chilis.com.mx/ubicaciones"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//select[@class="form-control location-search-results animated fadeIn input-bg--white"]/option'
    )
    for d in div:
        slug = "".join(d.xpath(".//@value"))
        if not slug:
            continue
        page_url = f"https://chilis.com.mx/ubicaciones/{slug}"
        city = "".join(d.xpath(".//text()"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        jsblock = (
            "".join(
                tree.xpath('//script[contains(text(), "var ubicaciones = ")]/text()')
            )
            .split("var ubicaciones = ")[1]
            .split(";")[0]
            .strip()
        )
        js = json.loads(jsblock)
        for j in js:

            location_name = j.get("tienda")
            ad = "".join(j.get("direccion"))
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            if location_name == "Paseo Querétaro":
                street_address = ad
            state = "<MISSING>"
            postal = a.postcode or "<MISSING>"
            postal = (
                postal.replace("C.P.", "")
                .replace("CP.", "")
                .replace("CP", "")
                .replace("C.P", "")
                .strip()
            )
            country_code = "MX"
            latitude = j.get("pin").get("lat")
            longitude = j.get("pin").get("lng")
            phone = "".join(j.get("telefono")) or "<MISSING>"
            if phone.find("<br>") != -1:
                phone = phone.split("<br>")[0].strip()
            if phone.find(",") != -1:
                phone = phone.split(",")[0].strip()
            if phone.find("-") != -1:
                phone = phone.split("-")[0].strip()
            hours_of_operation = " ".join(j.get("horarios")) or "<MISSING>"

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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
