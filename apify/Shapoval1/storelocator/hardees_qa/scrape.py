import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hardees.qa/"
    api_url = "https://www.google.com/maps/d/embed?mid=1knF9b47nuuomZYuulWMTaNtDwSQ&ll=25.429489536670854%2C51.476563700000014&z=9"
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
        page_url = "https://www.hardees.qa/find-a-hardees"
        location_name = l[5][0][1][0]
        street_address = l[5][3][6][1][0]
        country_code = "Qatar"
        latitude = l[1][0][0][0]
        longitude = l[1][0][0][1]
        phone = l[5][3][5][1][0]
        hours_of_operation = (
            str(l[5][3][1][:2])
            + " "
            + str(l[5][3][2][:2])
            + " "
            + str(l[5][3][3][:2])
            + " "
            + str(l[5][3][4][:2])
        )
        hours_of_operation = (
            "".join(hours_of_operation)
            .replace("[", "")
            .replace("]] ", ",")
            .replace("'", "")
            .replace(", ", ": ")
            .replace("]]", "")
            .strip()
        )

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
