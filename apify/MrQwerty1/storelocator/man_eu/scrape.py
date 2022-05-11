from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_ids():
    ids = []
    r = session.get(
        "https://settlement.man.eu/settlement/public/mui/world.js?", headers=headers
    )
    js = r.json()
    for j in js:
        ids.append(j[0])

    return ids


def get_data(store_number, sgw: SgWriter):
    api = f"https://settlement.man.eu/settlement/public/mui/detail?id={store_number}"
    page_url = f"https://settlement.man.eu/settlement/public/client/detail.html?lang=en&id={store_number}"
    r = session.get(api, headers=headers)
    j = r.json()

    location_name = j[1][0]
    raw_address = ", ".join(j[2])
    street_address = j[2][0]
    city = j[2][2]
    postal = j[2][1]
    country_code = j[2][3]
    try:
        phone = j[4][0]
    except:
        phone = SgRecord.MISSING
    try:
        latitude = j[3][1]
    except IndexError:
        latitude = SgRecord.MISSING
    try:
        longitude = j[3][0]
    except IndexError:
        longitude = SgRecord.MISSING

    _tmp = []
    hours = j[13]
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    for hoo, day in zip(hours, days):
        hoo = list(filter(None, [h for h in hoo]))
        if not hoo:
            continue

        hoo = hoo.pop(0)
        hoo = list(filter(None, [h.strip() for h in hoo]))
        if hoo[0] == "--":
            _tmp.append(f"{day}: Closed")
            continue

        inter = "-".join(hoo)
        if inter.count("-") == 7:
            inter = inter.replace("------", "")
        if inter.count("-") == 3:
            inter = inter[:11] + "|" + inter[12:]
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()
    # ids = ['66645', '66424', '44347', '40164']

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.man.eu/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
