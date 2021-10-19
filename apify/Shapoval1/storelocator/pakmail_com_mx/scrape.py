import json
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.pakmail.com.mx/"
    api_url = "https://engine.aceleradordigitaldenegocios.com.mx/sucursalesPakmail"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        slug = "".join(j.get("sitio"))
        if slug.find("plaza-samara-.pakmail.com.mx") != -1:
            slug = "plaza-samara.pakmail.com.mx"
        page_url = f"https://{slug}"

        location_name = j.get("name") or "<MISSING>"
        ad = "".join(j.get("address"))
        store_number = j.get("mx") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if phone == "<MISSING>":
            phone = j.get("phone2") or "<MISSING>"
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        if street_address.find("Estado De México") != -1:
            state = "Estado De México"
            street_address = street_address.replace("Estado De México", "").strip()
        if street_address == "5 Loc.":
            street_address = " ".join(ad.split(",")[:2]).strip()
        postal = a.postcode or "<MISSING>"
        if postal.find(" ") != -1:
            postal = postal.split()[-1].strip()
        country_code = "MX"
        city = a.city or "<MISSING>"

        r = session.get(page_url, headers=headers)
        time.sleep(5)
        tree = html.fromstring(r.text)
        jsblock = (
            "".join(
                tree.xpath('//script[contains(@type, "application/ld+json")]/text()')
            )
            .replace("//<![CDATA[", "")
            .replace("//]]>", "")
        )
        js = json.loads(jsblock)
        hours_of_operation = (
            "".join(js.get("openingHours")).replace("[", "").replace("]", "").strip()
        )
        hours_of_operation = (
            hours_of_operation.replace('",', ",").replace('"', "").strip()
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
            store_number=store_number,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
