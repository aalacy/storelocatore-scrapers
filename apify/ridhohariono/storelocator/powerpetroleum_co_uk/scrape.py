import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://powerpetroleum.co.uk/"
    api_url = "https://www.google.com/maps/d/u/0/embed?mid=1FdU4QYBZifAa4BTon9Ij4bKSOdYd9mZz&ehbc=2E312F&test&ll=50.87578480972796%2C0.071363343554669&z=10"
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
        page_url = "https://www.local-fuels.co.uk/locations"
        location_name = "".join(l[5][0][1][0]).replace("u0027", "`")
        info = str(l[5][1][1][0])
        ad = info.split("#")[1].strip()
        street_address = "<MISSING>"
        city = "<MISSING>"
        if ad.count("-") == 2:
            street_address = ad.split("-")[0].strip()
            city = ad.split("-")[1].strip()
        if ad.count("-") == 1:
            city = ad.split("-")[0].strip()
        if ad.find(",") != -1:
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].split("-")[0].strip()
        postal = ad.split("-")[-1].strip()
        country_code = "UK"
        latitude = l[1][0][0][0]
        longitude = l[1][0][0][1]
        phone = info.split("#")[2].strip()
        hours_of_operation = info.split("Opening Hours#")[1].split("#")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
