import json
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kellerlogistics.com"
    api_url = "https://www.google.com/maps/d/embed?mid=1AiYcgzVuftfkcloKe7ggeZehgfI&ll=37.80993328494997%2C-103.36728791599614&z=5"
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

        page_url = "https://kellerlogistics.com/warehousing/facilities/"
        location_name = l[5][0][1][0]
        street_address = "".join(l[5][3][0][1])
        state = "".join(l[5][3][2][1])
        postal = "".join(l[5][3][3][1])
        country_code = "US"
        city = "".join(l[5][3][1][1])
        latitude = l[1][0][0][0]
        longitude = l[1][0][0][1]
        try:
            phone = "".join(l[5][3][4][1])
        except:
            phone = "<MISSING>"
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
        if state == "OH":
            page_url = "https://kellerlogistics.com/warehousing/facilities/ohio/"
        if state == "TX":
            page_url = "https://kellerlogistics.com/warehousing/facilities/texas/"
        if state == "GA":
            page_url = "https://kellerlogistics.com/warehousing/facilities/georgia/"
        if state == "KY":
            page_url = "https://kellerlogistics.com/warehousing/facilities/kentucky/"
        if state == "IL":
            page_url = "https://kellerlogistics.com/warehousing/facilities/illinois/"
        r = session.get(
            "https://kellerlogistics.com/warehousing/facilities/", headers=headers
        )
        try:
            tree = html.fromstring(r.text)
        except:
            time.sleep(5)
            r = session.get(
                "https://kellerlogistics.com/warehousing/facilities/", headers=headers
            )
            tree = html.fromstring(r.text)
        phone = "".join(tree.xpath('//span[@id="et-info-phone"]/text()'))

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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
