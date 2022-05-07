from concurrent import futures
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def generate_links():
    r = session.get("https://stores.shopversona.com/index.json")
    js = r.json()["directoryHierarchy"]
    url = list(get_urls(js))
    urls = []
    for i in url:
        i = i.replace(".html", "")
        urls.append(i)
    return urls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://stores.shopversona.com/{state['url']}.json"
        else:
            yield from get_urls(children)


def get_data(url, sgw: SgWriter):

    r = session.get(url)
    j = r.json()["profile"]
    a = j.get("address")
    locator_domain = "https://shopversona.com/"
    page_url = url.replace(".json", "")
    location_name = j.get("c_aboutTitle") or j.get("name") or "<MISSING>"
    street_address = f"{a.get('line1')} {a.get('line2') or ''}".replace(
        "None", ""
    ).strip()
    city = a.get("city") or "<MISSING>"
    state = a.get("region") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = a.get("countryCode") or "<MISSING>"
    try:
        phone = j.get("mainPhone").get("display") or "<MISSING>"
    except:
        phone = "<MISSING>"
    latitude = j.get("yextDisplayCoordinate").get("lat")
    longitude = j.get("yextDisplayCoordinate").get("long")
    days = j.get("hours", {}).get("normalHours") or []

    _tmp = []
    for d in days:
        day = d.get("day")[:3].capitalize()
        try:
            interval = d.get("intervals")[0]
            start = str(interval.get("start"))
            end = str(interval.get("end"))

            if len(start) == 3:
                start = f"0{start}"

            if len(end) == 3:
                end = f"0{end}"

            line = f"{day}  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"

        except IndexError:
            line = f"{day}  Closed"

        _tmp.append(line)

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if (
        hours_of_operation.count("Closed") == 7
        or location_name.lower().find("closed") != -1
    ):
        hours_of_operation = "Closed"
    if hours_of_operation.count("0: - 0:") == 7:
        hours_of_operation = "Open 24 Hours"

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
        raw_address=f"{street_address} {city}, {state} {postal}",
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = generate_links()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
