from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(0, 100000, 50):
        r = session.get(
            f"https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=2500&location=68801&limit=50&api_key=8dd26f0d852e72960993b99328db0505&v=20181201&offset={i}&searchIds=6331&filter="
            + '{"c_resellerStore":{"$eq":false}}',
            headers=headers,
        )
        js = r.json()["response"]["entities"]

        for j in js:
            a = j.get("address") or {}
            adr1 = a.get("line1") or ""
            adr2 = a.get("line2") or ""
            street_address = f"{adr1} {adr2}".strip()
            city = a.get("city")
            state = a.get("region")
            postal = a.get("postalCode")
            country_code = a.get("countryCode")
            location_name = f"{j.get('name')} {j.get('c_mallName') or ''}".strip()
            page_url = j.get("landingPageUrl")
            phone = j.get("mainPhone")

            g = j.get("yextDisplayCoordinate") or {}
            latitude = g.get("latitude")
            longitude = g.get("longitude")

            hours = j.get("hours")
            _tmp = []
            for k, v in hours.items():
                if k == "holidayHours":
                    continue
                if isinstance(v, str):
                    continue

                day = k
                isclosed = v.get("isClosed")
                if isclosed:
                    _tmp.append(f"{day.capitalize()}: Closed")
                    continue
                interval = v.get("openIntervals")[0]
                start = interval.get("start")
                end = interval.get("end")
                _tmp.append(f"{day.capitalize()}: {start} - {end}")

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

        if len(js) < 50:
            break


if __name__ == "__main__":
    locator_domain = "https://casper.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
