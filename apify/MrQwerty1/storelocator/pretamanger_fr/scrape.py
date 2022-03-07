from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def generate_links():
    r = session.get("https://locations.pretamanger.fr/index.json")
    js = r.json()["directoryHierarchy"]
    urls = list(get_urls(js))

    return urls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://locations.pretamanger.fr/{state['url']}.json"
        else:
            yield from get_urls(children)


def get_data(url, sgw: SgWriter):
    r = session.get(url)
    j = r.json()["profile"]

    page_url = url.replace(".json", "")
    location_name = j.get("geomodifier") or ""
    a = j.get("address")

    street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
    city = a.get("city")
    state = a.get("region")
    postal = a.get("postalCode")
    country_code = a.get("countryCode")
    store_number = j.get("corporateCode")
    try:
        phone = j["mainPhone"]["display"]
    except KeyError:
        phone = SgRecord.MISSING

    latitude = j["yextDisplayCoordinate"]["lat"]
    longitude = j["yextDisplayCoordinate"]["long"]
    try:
        days = j["hours"]["normalHours"]
    except KeyError:
        days = []

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

            if start == "0":
                start = "1200"

            line = f"{day}:  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
        except IndexError:
            line = f"{day}:  Closed"

        _tmp.append(line)

    hours_of_operation = ";".join(_tmp)
    if (
        hours_of_operation.count("Closed") == 7
        or location_name.lower().find("closed") != -1
    ):
        hours_of_operation = "Closed"

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
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = generate_links()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.pretamanger.fr/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
