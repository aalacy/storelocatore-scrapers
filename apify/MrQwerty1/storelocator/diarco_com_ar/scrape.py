from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://www.diarco.com.ar/map"
    r = session.get(api, headers=headers)
    js = r.json()["nodes"]

    for j in js:
        j = j["node"]
        source = j.get("body") or "<html/>"
        tree = html.fromstring(source)
        line = tree.xpath("//text()")
        line = list(filter(None, [li.replace("\xa0", " ").strip() for li in line]))

        postal = SgRecord.MISSING
        phone = SgRecord.MISSING
        cnt = 0
        for li in line:
            if "código postal" in li.lower():
                postal = (
                    li.lower()
                    .replace("código postal:", "")
                    .replace(".", "")
                    .replace("​ ", "")
                    .strip()
                )
            if "contacto" in li.lower():
                phone = line[cnt + 1].replace("Tel:", "").strip()
                if phone[-1].isalpha():
                    phone = SgRecord.MISSING
                if "/" in phone:
                    phone = phone.split("/")[0]
            cnt += 1

        adr = line.pop(1).replace(".", "").strip()
        street_address, city = SgRecord.MISSING, SgRecord.MISSING
        if "-" in adr:
            city = adr.split("-")[-1].strip()
            if "," in city:
                city = city.split(",")[0].strip()
            street_address = "-".join(adr.split("-")[:-1]).strip()
        elif "," in adr and adr[-1].isalpha():
            city = adr.split(",")[-1].strip()
            street_address = ",".join(adr.split(",")[:-1]).strip()
        else:
            street_address = adr

        state = j.get("province")
        country_code = "AR"
        location_name = j.get("title")
        latitude = j.get("lat")
        longitude = j.get("lng")

        hours = tree.xpath("//*[contains(text(), 'Horario')]/following-sibling::text()")
        hours_of_operation = ";".join(hours).replace("\xa0", " ").replace(".", "")
        if "2022" in hours_of_operation:
            hours_of_operation = "Temporarily Closed"

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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.diarco.com.ar/"
    page_url = "https://www.diarco.com.ar/sucursales"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
