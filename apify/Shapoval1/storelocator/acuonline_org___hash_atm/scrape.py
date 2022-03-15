import geonamescache
from sgscrape.pause_resume import CrawlStateSingleton
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    gc = geonamescache.GeonamesCache()
    c = gc.get_cities()
    US_cities = [
        c[key]["name"] for key in list(c.keys()) if c[key]["countrycode"] == "US"
    ]
    return US_cities


def get_data(url, sgw: SgWriter):
    locator_domain = "https://acuonline.org/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://03919locator.wave2.io",
        "Connection": "keep-alive",
        "Referer": "https://03919locator.wave2.io/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
    }

    data = (
        '{"Latitude":"","Longitude":"","Address":"'
        + url
        + '","City":"","State":"","Zipcode":"","Country":"","Action":"textsearch","ActionCategory":"web","Filters":"FCS,FIITM,FIATM,ATMSF,ATMDP,ESC,"}'
    )

    r = session.post(
        "https://locationapi.wave2.io/api/client/getlocations",
        headers=headers,
        data=data,
    )
    js = r.json()["Features"]
    if not js:
        return
    for j in js:

        page_url = "https://www.acuonline.org/home/resources/locations"
        a = j.get("Properties")
        location_name = a.get("LocationName") or "<MISSING>"
        street_address = a.get("Address") or "<MISSING>"
        city = a.get("City") or "<MISSING>"
        state = a.get("State") or "<MISSING>"
        postal = a.get("Postalcode") or "<MISSING>"
        if postal == "0":
            postal = "<MISSING>"
        country_code = a.get("Country") or "<MISSING>"
        store_number = a.get("LocationId")
        phone = "<MISSING>"
        latitude = a.get("Latitude") or "<MISSING>"
        longitude = a.get("Longitude") or "<MISSING>"
        location_type = a.get("LocationCategory") or "<MISSING>"
        hours_of_operation = (
            j.get("LocationFeatures").get("TwentyFourHours") or "<MISSING>"
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)

    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
