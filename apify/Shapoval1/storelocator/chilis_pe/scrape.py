import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.chilis.pe/"
    api_url = "https://www.google.com/maps/d/u/0/embed?hl=es-419&ll=-12.067868538424731%2C-76.99936319562985&z=12&mid=16UfWGGF1Nnbhb3B0AFfiC08-JYPhDrxt"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    cleaned = (
        r.text.replace("\\t", " ")
        .replace("\t", " ")
        .replace("\\n]", "]")
        .replace("\n]", "]")
        .replace("\\n,", ",")
        .replace("\\n", "#")
        .replace('\\"', '"')
        .replace("\\u003d", "=")
        .replace("\\u0026", "&")
        .replace("\\", "")
        .replace("\xa0", " ")
    )

    locations = json.loads(
        cleaned.split('var _pageData = "')[1].split('";</script>')[0]
    )[1][6][2][12][0][13][0]
    for l in locations:

        page_url = "https://www.chilis.pe/estatico/zonasreparto"
        location_name = l[5][0][1][0]
        try:
            ad = l[5][1][1][0]
        except TypeError:
            ad = "<MISSING>"
        street_address = "<MISSING>"
        if ad != "<MISSING>":
            street_address = (
                ad.split("#📍")[1]
                .split("Teléfono")[0]
                .replace("#", " ")
                .replace("📞", "")
                .strip()
            )
        country_code = "PE"
        latitude = l[1][0][0][0]
        longitude = l[1][0][0][1]
        phone = "<MISSING>"
        if ad != "<MISSING>":
            phone = ad.split("Teléfono:")[1].split("#")[0].strip()
        hours_of_operation = "<MISSING>"
        if ad != "<MISSING>":
            hours_of_operation = (
                ad.split("llevar#")[1].split("✔️Delivery")[0].replace("#", " ").strip()
            )
        info = str(location_name).split()
        store_number = "<MISSING>"
        for i in info:
            if i.isdigit():
                store_number = i

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=SgRecord.MISSING,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
