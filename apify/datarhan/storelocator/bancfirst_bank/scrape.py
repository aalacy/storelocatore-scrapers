from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests(verify_ssl=False)
    start_url = "https://www.bancfirst.bank/locations"
    domain = "bancfirst.bank"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    session.get(start_url, headers=hdr)

    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://05362locator.wave2.io",
        "Connection": "keep-alive",
        "Referer": "https://05362locator.wave2.io/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers",
    }
    hdr_options = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
        "Referer": "https://05362locator.wave2.io/",
        "Origin": "https://05362locator.wave2.io",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers",
    }
    url = "https://locationapi.wave2.io/api/client/getlocations"
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=30
    )
    for code in all_codes:
        frm = {
            "Action": "textsearch",
            "ActionCategory": "web",
            "Address": code,
            "City": "",
            "Country": "",
            "Filters": "FCS,",
            "Latitude": "",
            "Longitude": "",
            "State": "",
            "Zipcode": "",
        }
        data = session.post(url, json=frm, headers=hdr_options).json()
        for poi in data["Features"]:
            location_type = poi["LocationFeatures"]["LocationType"]
            hoo = ""
            if location_type == "BancFirst Branch":
                monday = f'Mon: {poi["Properties"]["MonOpen"]} - {poi["Properties"]["MonClose"]}'
                tuesday = f'Tue: {poi["Properties"]["TueOpen"]} - {poi["Properties"]["TueClose"]}'
                wednesday = f'Wed: {poi["Properties"]["WedOpen"]} - {poi["Properties"]["WedClose"]}'
                thursday = f'Thu: {poi["Properties"]["ThuOpen"]} - {poi["Properties"]["ThuClose"]}'
                friday = f'Fri: {poi["Properties"]["FriOpen"]} - {poi["Properties"]["FriClose"]}'
                saturday = "Sat: closed"
                if poi["Properties"]["SatOpen"]:
                    saturday = f'Sat: {poi["Properties"]["SatOpen"]} - {poi["Properties"]["SatClose"]}'
                sunday = "Sun: closed"
                if poi["Properties"]["SunOpen"]:
                    sunday = f'Sun: {poi["Properties"]["SunOpen"]} - {poi["Properties"]["SunClose"]}'
                hoo = f"{monday} {tuesday} {wednesday} {thursday} {friday} {saturday} {sunday}"

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=poi["Properties"]["LocationName"],
                street_address=poi["Properties"]["Address"],
                city=poi["Properties"]["City"],
                state=poi["Properties"]["State"],
                zip_postal=poi["Properties"]["Postalcode"],
                country_code=poi["Properties"]["Country"],
                store_number=poi["Properties"]["LocationId"],
                phone=poi["Properties"]["Phone"],
                location_type=location_type,
                latitude=poi["Properties"]["Latitude"],
                longitude=poi["Properties"]["Longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
