import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()

    return street


def get_full(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def get_adr():
    out = dict()
    r = session.get("https://www.woolworths.co.za/storelocator", headers=headers)
    tree = html.fromstring(r.text)
    script = "".join(
        tree.xpath("//script[contains(text(), '__INITIAL_STATE__')]/text()")
    )
    js = json.loads(script.split("__INITIAL_STATE__ =")[1])
    js = js["header"]["headerDetails"]["regions"]["suburbs"]
    for k, v in js.items():
        city = k.split(",")[0].strip()
        state = k.split(",")[-1].strip()
        _id = v.get("id")
        postal = v.get("postalCode")
        out[_id] = {"city": city, "postal": postal, "state": state}

    return out


def fetch_data(sgw: SgWriter):
    adr = get_adr()
    api = "https://www.woolworths.co.za/server/storelocatorByArea?suburbId=3000&distance=5000"
    r = session.get(api, headers=headers)
    js = r.json()["stores"]

    for j in js:
        raw_address = j.get("storeAddress") or ""
        raw_address = " ".join(raw_address.split())
        if raw_address.endswith(","):
            raw_address = raw_address[:-1]
        key = j.get("suburbId") or ""
        a = adr.get(key) or {}
        if a:
            street_address = get_international(raw_address)
            city = a.get("city")
            state = a.get("state")
            postal = a.get("postal")
        else:
            street_address, city, state, postal = get_full(raw_address)

        if len(street_address) < 8:
            street_address = raw_address.split(",")[0]
        country_code = "ZA"
        store_number = j.get("storeId")
        location_name = str(j.get("storeName")).strip()
        phone = j.get("phoneNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        hours = j.get("openingHours") or []
        for h in hours:
            day = h.get("day")
            inter = h.get("hours") or ""
            inter = inter.replace("h", ":")
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.woolworths.co.za/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.woolworths.co.za/storelocator",
        "X-Requested-By": "Woolworths Online",
        "X-Frame-Options": "SAMEORIGIN",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
