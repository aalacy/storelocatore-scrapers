import re
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_slug():
    r = session.get("https://www.decathlon.sg/s/our-stores", headers=headers)
    return re.findall(r'"buildId":"(.+?)"', r.text).pop(0)


def get_pages():
    pages = dict()
    slug = get_slug()
    api = f"https://www.decathlon.sg/_next/data/{slug}/s/our-stores.json"
    r = session.get(api, headers=headers)
    js = r.json()["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"][0][
        "fields"
    ]["floor"][0]["fields"]["storeList"]
    for j in js:
        _id = j["fields"]["storeId"]
        link = j["fields"]["ctaLink"]
        pages[_id] = link

    return pages


def fetch_data(sgw: SgWriter):
    api = "https://storesetting-prod.decathlon.sg/api/v1/stores"
    black = ["water", "city", ", north", "esr", "the ", ", tiong", "west"]
    pages = get_pages()
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("name") or ""
        location_name = location_name.replace("\u200b", "")
        store_number = j.get("id")
        slug = pages.get(store_number)
        page_url = f"https://www.decathlon.sg{slug}"
        phone = j.get("phone1") or ""
        if len(phone) < 5:
            phone = SgRecord.MISSING

        a = j.get("address") or {}
        street_address = a.get("street") or ""
        for b in black:
            if b in street_address.lower():
                street_address = street_address.lower().split(b)[0].title().strip()
                break

        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = a.get("city")
        state = a.get("region") or ""
        state = state.split()[-1]
        postal = a.get("postalCode")
        latitude = a.get("latitude")
        longitude = a.get("longitude")

        _tmp = []
        hours = j.get("workingHours") or []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for h in hours:
            i = h.get("day") or 0
            if i:
                day = days[i - 1]
            else:
                continue
            start = h.get("open")
            end = h.get("close")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="SG",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.decathlon.sg/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
