from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


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
    frm = {
        "Action": "textsearch",
        "ActionCategory": "web",
        "Address": "Oklahoma",
        "City": "",
        "Country": "",
        "Filters": "FCS,FIATM,ATMSF,ATMDP,",
        "Latitude": "",
        "Longitude": "",
        "State": "",
        "Zipcode": "",
    }
    data = session.post(url, json=frm, headers=hdr_options).json()
    for poi in data["Features"]:
        location_type = poi["LocationFeatures"]["LocationType"]
        if location_type != "BancFirst ATM":
            continue

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
            hours_of_operation="",
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
