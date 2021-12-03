import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda.com.np"
    api_url = "https://www.google.com/maps/d/u/5/embed?mid=1Ji--VLSKchHZqQw0tBwREYOsI4BMqqiP&ll=-3.81666561775622e-14%2C85.8764535546494&z=1"
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
    )[1][6][0][12][0][13][0]

    for l in locations:
        page_url = "https://honda.com.np/dealer-locations/"
        location_name = l[5][0][1][0]
        location_type = "Automobile Dealer"
        street_address = l[5][3][0][1][0]
        country_code = "Nepal"
        latitude = l[1][0][0][0]
        longitude = l[1][0][0][1]
        phone = str(l[5][3][2][1][0])
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=SgRecord.MISSING,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
