import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.coppel.com.ar"
    page_url = "https://www.coppel.com.ar/nuestras-tiendas"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "__RUNTIME__")]/text()'))
        .split('"tiendas":')[1]
        .split('},"render"')[0]
        .strip()
    )

    js = json.loads(js_block)
    for j in js:

        location_name = j.get("nombre") or "<MISSING>"
        ad = j.get("direccion")
        street_address = (
            " ".join(str(ad).split(",")[:-1]).replace("Buenos Aires", "").strip()
        )
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        state = "<MISSING>"
        postal = str(ad).split("CP:")[1].replace(".", "").strip()
        country_code = "AR"
        adr = str(ad).split(",")[-1].strip()
        city = adr.split("CP")[0].replace(".", "").strip()
        store_number = str(location_name).split()[0].strip()
        text = j.get("linkMaps")
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = j.get("horario") or "<MISSING>"

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
            phone=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
