from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(0, 100000, 20):
        r = session.get(
            f"https://stores.primark.com/search?q=&offset={i}", headers=headers
        )
        js = r.json()["response"]["entities"]
        for jj in js:
            j = jj.get("profile")
            a = j.get("address")
            page_url = (
                j.get("websiteUrl") if j.get("websiteUrl") else j.get("c_pagesURL")
            )
            page_url = page_url.split("?")[0]
            street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
            city = a.get("city")
            location_name = f"{j.get('name')} {j.get('c_geomodifier') or ''}".strip()
            state = a.get("region")
            postal = a.get("postalCode")
            country_code = a.get("countryCode")
            phone = j.get("mainPhone", {}).get("display")
            latitude = j.get("yextDisplayCoordinate", {}).get("lat")
            longitude = j.get("yextDisplayCoordinate", {}).get("long")

            hours = j.get("hours", {}).get("normalHours", [])
            _tmp = []
            for h in hours:
                day = h.get("day")
                if not h.get("isClosed"):
                    interval = h.get("intervals")
                    start = str(interval[0].get("start"))
                    if len(start) == 3:
                        start = f"0{start}"
                    end = str(interval[0].get("end"))
                    line = f"{day[:3].capitalize()}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
                else:
                    line = f"{day[:3].capitalize()}: Closed"
                _tmp.append(line)

            hours_of_operation = ";".join(_tmp)
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
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 20:
            break


if __name__ == "__main__":
    locator_domain = "https://www.primark.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
