from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome


def get_locations(session, offset):
    return session.execute_async_script(
        f"""
        fetch("https://local.directauto.com/search?offset={offset}&l=en", {{
            "credentials": "include",
            "headers": {{
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.5",
                "Alt-Used": "local.directauto.com",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            }},
            "referrer": "https://local.directauto.com/search",
            "method": "GET",
            "mode": "cors"
        }})
            .then(res => res.json())
            .then(arguments[0])
            .catch(err => arguments[0](JSON.stringify(err.error)))
    """
    )


def fetch_data(sgw: SgWriter):
    with SgChrome(is_headless=True) as session:
        session.set_page_load_timeout(600)
        session.set_script_timeout(300)
        page_url = "https://local.directauto.com/"
        try:
            session.get(page_url)
        except:
            pass

        for cnt in range(0, 5000, 10):
            result = get_locations(session, cnt)

            js = result["response"]["entities"]

            for j in js:
                j = j.get("profile") or {}
                desc = j.get("description") or ""
                if "permanently closed" in desc:
                    continue

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
                location_name = j.get("name") or ""
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
                if "closed" not in location_name.lower() and not hours_of_operation:
                    continue

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
    locator_domain = "https://directauto.com/"

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
