from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://negozi.vodafone.it/search"
    for i in range(0, 5000, 10):
        params = {
            "r": "19",
            "storeType": [
                "5627834",
                "5655633",
            ],
            "offset": str(i),
        }
        r = session.get(api, headers=headers, params=params)
        js = r.json()["response"]["entities"]

        for j in js:
            j = j.get("profile")
            location_name = j.get("name")
            page_url = j.get("c_pagesURL")
            a = j.get("address")

            street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
            city = a.get("city")
            state = a.get("region")
            postal = a.get("postalCode")
            country_code = a.get("countryCode")
            store_number = j.get("corporateCode")
            try:
                phone = j["mainPhone"]["display"]
            except:
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
                    start = str(interval.get("start")).zfill(4)
                    end = str(interval.get("end")).zfill(4)

                    if start == "0000":
                        start = "1200"

                    line = f"{day}:  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
                except IndexError:
                    line = f"{day}:  Closed"

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
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 10:
            break


if __name__ == "__main__":
    locator_domain = "https://negozi.vodafone.it/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "application/json",
        "Referer": "https://negozi.vodafone.it/abbiategrasso?ourl=https%3A%2F%2Fnegozi.vodafone.it%2Fabbiategrasso%2Fvodafone-multiservizi-abbiategrasso.json&oref=",
        "Alt-Used": "negozi.vodafone.it",
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
