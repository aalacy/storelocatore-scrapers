from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://stores.jcrew.com/search"

    for cnt in range(0, 5000, 10):
        params = {
            "l": "en",
            "offset": str(cnt),
        }
        r = session.get(api, headers=headers, params=params)
        js = r.json()["response"]["entities"]

        for j in js:
            j = j.get("profile") or {}

            a = j.get("address") or {}
            adr1 = a.get("line1") or ""
            adr2 = a.get("line2") or ""
            street_address = f"{adr1} {adr2}".strip()
            city = a.get("city")
            state = a.get("region")
            postal = a.get("postalCode")
            country_code = "US"
            try:
                store_number = j["meta"]["id"]
            except KeyError:
                store_number = SgRecord.MISSING
            location_name = j.get("name")
            page_url = j.get("c_pagesURL")

            try:
                phone = j["mainPhone"]["display"]
            except KeyError:
                phone = SgRecord.MISSING

            g = j.get("yextDisplayCoordinate") or {}
            latitude = g.get("lat")
            longitude = g.get("long")

            _tmp = []
            try:
                hours = j["hours"]["normalHours"]
            except:
                hours = []

            for h in hours:
                day = h.get("day")
                isclosed = h.get("isClosed")
                if isclosed:
                    _tmp.append(f"{day}: Closed")
                    continue

                try:
                    i = h["intervals"][0]
                except:
                    i = dict()

                start = str(i.get("start") or "").zfill(4)
                end = str(i.get("end") or "").zfill(4)
                start = start[:2] + ":" + start[2:]
                end = end[:2] + ":" + end[2:]
                if start != end:
                    _tmp.append(f"{day}: {start}-{end}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)

        if len(js) < 10:
            break


if __name__ == "__main__":
    locator_domain = "https://jcrew.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "application/json",
        "Referer": "https://stores.jcrew.com/",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
