from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.optumcare.com/bin/optumcare/findlocations"
    domain = "optumcare.com"
    hdr = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "CSRF-Token": "undefined",
        "Host": "www.optumcare.com",
        "Referer": "https://www.optumcare.com/content/optumcare3/en/state-networks/locations/ocnu/locations-nav/provider-lookup/provider-search-results.html?isAcceptingNewPatients=true&radius=5&network=OCUT",
        "Origin": "https://www.optumcare.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    frm = {"network": "OCUT", "sort": "ascending"}
    data = session.post(start_url, headers=hdr, json=frm).json()

    all_locations = data["result"]["data"]["providers"]["hits"]
    for poi in all_locations:
        location_name = poi["provider"]["providerInfo"]["businessName"]
        street_address = poi["provider"]["locations"][0]["addressInfo"]["line1"]
        city = poi["provider"]["locations"][0]["addressInfo"]["city"]
        state = poi["provider"]["locations"][0]["addressInfo"]["state"]
        zip_code = poi["provider"]["locations"][0]["addressInfo"]["zip"]
        geo = poi["provider"]["locations"][0]["addressInfo"]["lat_lon"].split(",")
        phone = ""
        if poi["provider"]["locations"][0].get("telephoneNumbers"):
            phone = [
                e
                for e in poi["provider"]["locations"][0]["telephoneNumbers"]
                if e["telephoneUsage"] == "Office Phone"
            ][0]["telephoneNumber"]

        item = SgRecord(
            locator_domain=domain,
            page_url="",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
