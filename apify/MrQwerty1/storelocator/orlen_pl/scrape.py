from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_ids():
    ids = []
    params = {
        "key": "DC30EA3C-D0D0-4D4C-B75E-A477BA236ACA",
        "format": "jsonp",
        "languageCode": "PL",
        "gasStationType": "",
        "services": "",
        "tags": "",
        "polyline": "",
        "keyWords": "",
        "food": "",
        "cards": "",
        "topN": "100",
        "automaticallyIncreaseDistanceRadius": "true",
        "sessionId": token,
    }
    r = session.get(
        "https://wsp.orlen.pl/plugin/GasStations.svc/FindPOI",
        headers=headers,
        params=params,
    )
    js = r.json()["Results"]
    for j in js:
        ids.append(j.get("Id"))

    return ids


def get_session():
    api = "https://wsp.orlen.pl/plugin/GasStations.svc/GetPluginBaseConfig?key=DC30EA3C-D0D0-4D4C-B75E-A477BA236ACA&format=jsonp&languageCode=PL"
    r = session.get(api, headers=headers)

    return r.json()["SessionId"]


def get_data(_id, sgw: SgWriter):
    params = {
        "key": "DC30EA3C-D0D0-4D4C-B75E-A477BA236ACA",
        "format": "jsonp",
        "languageCode": "PL",
        "gasStationId": _id,
        "gasStationTemplate": "DlaKierowcowTemplates",
        "sessionId": token,
    }
    api = "https://wsp.orlen.pl/plugin/GasStations.svc/GetGasStation"
    r = session.get(api, headers=headers, params=params)
    j = r.json()

    location_name = j.get("Name")
    adr1 = j.get("StreetAddress") or ""
    adr2 = j.get("StreetNumber") or ""
    if adr2 == "-":
        adr2 = ""

    street_address = f"ul. {adr1} {adr2}".strip()
    city = j.get("City")
    postal = j.get("PostalCode")
    country_code = j.get("Country")
    raw_address = " ".join(f"{street_address} {city} {postal} {country_code}".split())
    phone = j.get("Phone") or ""
    if ";" in phone:
        phone = phone.split(";")[0].strip()
    phone = phone.replace("-", "")
    latitude = j.get("Latitude")
    longitude = j.get("Longitude")

    store_number = j.get("LocalId")
    location_type = j.get("BrandTypeName")
    hours_of_operation = j.get("OpeningHours")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        location_type=location_type,
        locator_domain=locator_domain,
        raw_address=raw_address,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.orlen.pl/"
    page_url = "https://www.orlen.pl/pl/dla-ciebie/stacje?kw=&from=&to=&s=&wp=&dst=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "script",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
    }
    session = SgRequests()
    token = get_session()

    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.RAW_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
