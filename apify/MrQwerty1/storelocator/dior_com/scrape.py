from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_urls():
    urls = []
    r = session.get("https://www.dior.com/fashion/stores/en_us.json")
    js = r.json()["directoryHierarchy"].values()
    for j in js:
        slugs = j["children"].keys()
        for slug in slugs:
            urls.append(f"https://www.dior.com/fashion/stores/{slug}.json")

    return urls


def get_data(api, sgw: SgWriter):
    r = session.get(api)
    jss = r.json()["keys"]

    for js in jss:
        j = js["entity"]["profile"]
        a = j.get("address") or {}
        c = j.get("yextDisplayCoordinate") or {}

        adr1 = a.get("line1") or ""
        adr2 = a.get("line2") or ""
        street_address = " ".join(f"{adr1} {adr2}".split())
        city = a.get("city") or ""
        state = a.get("region") or ""
        postal = a.get("postalCode") or ""
        country = a.get("countryCode")
        raw_address = " ".join(f"{adr1} {adr2} {city} {state} {postal}".split())
        latitude = c.get("lat")
        longitude = c.get("long")
        location_name = j.get("c_locationName") or j.get("name")
        location_type = j.get("c_locationType")
        page_url = j.get("c_pagesURL") or api.replace(".json", "")

        try:
            phone = j["mainPhone"]["display"]
        except KeyError:
            phone = SgRecord.MISSING

        _tmp = []
        try:
            days = j["hours"]["normalHours"]
        except KeyError:
            days = []

        for d in days:
            day = d.get("day")
            try:
                interval = d.get("intervals")[0]
                start = str(interval.get("start")).zfill(4)
                end = str(interval.get("end")).zfill(4)
                line = f"{day}:  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
            except IndexError:
                line = f"{day}: Closed"
            _tmp.append(line)

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            phone=phone,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.dior.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
