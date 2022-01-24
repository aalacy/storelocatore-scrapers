from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(0, 100000, 50):
        r = session.get(
            f"https://stores.bang-olufsen.com/en/search?l=en&per=50&offset={i}",
            headers=headers,
        )
        js = r.json()["response"]["entities"]

        for jj in js:
            j = jj.get("profile")
            a = j.get("address")
            page_url = j.get("c_pagesURL")
            street_address = a.get("line1") or ""
            city = a.get("city") or ""
            location_name = f"Bang & Olufsen {city}"
            location_type = j.get("c_storeType")
            state = a.get("region")
            postal = a.get("postalCode")
            country_code = a.get("countryCode")
            phone = j.get("mainPhone", {}).get("display")
            latitude = j.get("yextDisplayCoordinate", {}).get("lat")
            longitude = j.get("yextDisplayCoordinate", {}).get("long")

            try:
                hours = j["hours"]["normalHours"]
            except KeyError:
                hours = []

            _tmp = []
            for h in hours:
                day = h.get("day")
                if not h.get("isClosed"):
                    interval = h.get("intervals")
                    start = str(interval[0].get("start"))
                    if len(start) == 3:
                        start = f"0{start}"
                    if len(start) == 1:
                        start = "1200"
                    end = str(interval[0].get("end"))
                    line = f"{day[:3].capitalize()}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
                else:
                    line = f"{day[:3].capitalize()}: Closed"
                _tmp.append(line)

            hours_of_operation = ";".join(_tmp)
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"
            if "Coming Soon" in location_name or j.get("c_comingSoon"):
                hours_of_operation = "Coming Soon"

            row = SgRecord(
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.replace("\n", ", "),
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                location_type=location_type,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 50:
            break


if __name__ == "__main__":
    locator_domain = "https://www.bang-olufsen.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
