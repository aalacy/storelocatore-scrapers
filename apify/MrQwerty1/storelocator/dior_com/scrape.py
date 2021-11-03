from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_ids():
    ids = []
    r = session.get("https://www.dior.com/store/json/posG.json")
    js = r.json()["items"]
    for j in js:
        ids.append(j[0])

    return ids


def generate_urls(ids):
    urls = []
    u = "https://tpc33of0na.execute-api.eu-west-1.amazonaws.com/prod/PointOfSale?ids="
    _tmp = []
    cnt = 0
    for i in ids:
        if cnt == 50:
            urls.append(f'{u}{",".join(_tmp)}')
            _tmp = []
            cnt = 0
        _tmp.append(i)
        cnt += 1

    urls.append(f'{u}{",".join(_tmp)}')
    return urls


def get_data(url, sgw: SgWriter):
    r = session.get(url)
    js = r.json()["Items"]

    for j in js:
        location_name = j.get("defaultName").replace("\n", " ").strip()
        ad1 = j.get("defaultStreet1") or ""
        ad2 = j.get("defaultStreet2") or ""
        ad1, ad2 = ad1.strip(), ad2.strip()
        if not ad2:
            street_address = ad1
        else:
            if ad1[0].isdigit():
                street_address = ad1
            else:
                street_address = f"{ad1} {ad2}".strip()

        if street_address.endswith(","):
            street_address = street_address[:-1]

        city = j.get("defaultCity")
        state = j.get("state")
        postal = j.get("defaultZipCode", "").strip()
        country_code = j.get("countryCode")

        if len(postal) > 5 and country_code == "US":
            state = postal.split()[0]
            postal = postal.split()[1]

        if len(postal) > 7 and country_code == "CA":
            state = postal.split()[0]
            postal = postal.replace(state, "").strip()

        phone = j.get("phoneNumber")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = j.get("calculatedWeeklyOpeningHours") or []

        for h in hours:
            index = h.get("day")
            day = days[int(index)]

            t = h.get("hours")
            if t:
                start = t[0].get("from")
                close = t[0].get("to")
            else:
                start, close = "", ""

            if start and start != close:
                _tmp.append(f"{day}: {start} - {close}")
            else:
                _tmp.append(f"{day}: Closed")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        row = SgRecord(
            page_url=SgRecord.MISSING,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()
    urls = generate_urls(ids)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.dior.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
