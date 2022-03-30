from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(0, 100000, 10):
        r = session.get(
            f"https://local.directauto.com/search?l=en&offset={i}", headers=headers
        )
        js = r.json()["response"]["entities"]

        for jj in js:
            j = jj.get("profile")
            a = j.get("address")
            street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
            city = a.get("city")
            location_name = j.get("name")
            state = a.get("region")
            postal = a.get("postalCode")
            country_code = a.get("countryCode")
            page_url = f'https://local.directauto.com/{jj.get("url")}'
            phone = j.get("mainPhone", {}).get("display")
            latitude = j.get("yextDisplayCoordinate", {}).get("lat")
            longitude = j.get("yextDisplayCoordinate", {}).get("long")

            hours = j.get("hours", {}).get("normalHours")
            _tmp = []
            for h in hours:
                day = h.get("day")
                if not h.get("isClosed"):
                    interval = h.get("intervals")
                    start = str(interval[0].get("start")).zfill(4)
                    end = str(interval[0].get("end")).zfill(4)
                    line = f"{day[:3].capitalize()}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
                else:
                    line = f"{day[:3].capitalize()}: Closed"
                _tmp.append(line)

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
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 10:
            break


if __name__ == "__main__":
    locator_domain = "https://directauto.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://local.directauto.com/search?q=",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
