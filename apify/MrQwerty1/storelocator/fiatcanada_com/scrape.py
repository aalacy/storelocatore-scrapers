from lxml import html
from concurrent import futures
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(code):
    _tmp = []
    url = f"https://www.fiatcanada.com/en/dealers/{code}"
    r = session.get(url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@id='sales-tab']//p[@class='C_DD-week-day']")
    for d in divs:
        day = "".join(d.xpath("./span[1]/text()")).strip()
        time = "".join(d.xpath("./span[last()]/text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data(sgw: SgWriter):
    codes = []
    hours = dict()
    api = "https://www.fiatcanada.com/data/dealers/expandable-radius?brand=fiat&longitude=-79.3984&latitude=43.7068&radius=5000"

    r = session.get(api, headers=headers)
    js = r.json()["dealers"]
    for j in js:
        codes.append(j.get("code"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, code): code for code in codes}
        for future in futures.as_completed(future_to_url):
            time = future.result()
            code = future_to_url[future]
            hours[code] = time

    for j in js:
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("province")
        postal = j.get("zipPostal")
        country_code = "CA"
        store_number = j.get("code")
        page_url = f"https://www.fiatcanada.com/en/dealers/{store_number}"
        location_name = j.get("name")
        phone = j.get("contactNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = hours.get(store_number)

        row = SgRecord(
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
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    }
    locator_domain = "https://www.fiatcanada.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
