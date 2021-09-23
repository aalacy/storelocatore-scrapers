import json
from sgscrape.sgpostal import International_Parser, parse_address
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://amestools.com"
    page_url = "https://amestools.com/store-locator/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    block = (
        "".join(tree.xpath('//script[@id="maplistko-js-extra"]/text()'))
        .split("var maplistScriptParamsKo = ")[1]
        .split("/*")[0]
        .replace("};", "}")
    )
    js = json.loads(block)
    for j in js["KOObject"][0]["locations"]:
        location_name = j.get("title")
        ad = j.get("address")
        ad = html.fromstring(ad)
        line = ad.xpath("//*//text()")
        line = list(filter(None, [a.strip() for a in line]))
        line = " ".join(line)
        if line.find("Phone:") != -1:
            line = line.split("Phone:")[0].strip()
        a = parse_address(International_Parser(), line)

        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        country_code = "US"
        if state == "AB" or state == "BC" or state == "MB" or state == "ON":
            country_code = "CA"
        postal = a.postcode or "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours = j.get("description")
        hours = html.fromstring(hours)
        hoo = " ".join(hours.xpath("//*//text()")).replace("\n", "").strip()

        try:
            phone = hoo.split("Phone:")[1].strip()
        except:
            phone = "<MISSING>"
        if phone.find("Email") != -1:
            phone = hoo.split("Email")[0].strip()
        if phone.find("Fax") != -1:
            phone = hoo.split("Fax")[0].strip()
        hours_of_operation = "<MISSING>"
        if hoo.find("Store Hours:") != -1:
            hours_of_operation = hoo.split("Store Hours:")[1]
        if phone.find("Phone:") != -1:
            phone = phone.split("Phone:")[1].strip()
        if hoo.find("COMING SOON") != -1:
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
