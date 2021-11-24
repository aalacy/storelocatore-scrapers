from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def generate_links():
    r = session.get("https://stores.ippudo.com/index.json")
    js = r.json()["directoryHierarchy"]

    urls = list(get_urls(js))
    return urls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://stores.ippudo.com/{state['url']}.json"
        else:
            yield from get_urls(children)


def get_data(url, sgw: SgWriter):

    r = session.get(url)
    j = r.json()["profile"]
    locator_domain = "https://ippudo.com/"
    page_url = url.replace(".json", "")
    a = j.get("address")
    location_name = j.get("name") or "<MISSING>"

    street_address = (
        f"{a.get('line1')} {a.get('line2') or ''} {a.get('line3') or ''}".replace(
            "None", ""
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    city = a.get("city") or "<MISSING>"
    state = a.get("region") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = a.get("countryCode") or "<MISSING>"
    try:
        phone = j.get("mainPhone").get("number") or "<MISSING>"
    except:
        phone = "<MISSING>"
    latitude = j.get("yextDisplayCoordinate").get("lat") or "<MISSING>"
    longitude = j.get("yextDisplayCoordinate").get("long") or "<MISSING>"
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
    store_number = "".join(j.get("c_pagesURL")).split("/")[-1].strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
