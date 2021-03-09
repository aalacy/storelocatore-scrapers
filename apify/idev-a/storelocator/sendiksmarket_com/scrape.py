from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from datetime import datetime
from datetime import timezone

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.sendiks.com",
    "referer": "https://www.sendiks.com/my-store",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.sendiks.com/"
        session_url = "https://api.freshop.com/2/sessions/create"
        utc_time = datetime.now().replace(tzinfo=timezone.utc)
        data = {
            "app_key": "sendiks",
            "referrer": "https://www.sendiks.com/my-store",
            "utc": str(utc_time.timestamp()),
        }
        token = session.post(session_url, data=data, headers=_headers).json()["token"]
        base_url = f"https://api.freshop.com/1/stores?app_key=sendiks&has_address=true&limit=-1&token={token}"
        locations = session.get(base_url).json()["items"]
        data = []
        for location in locations:
            street_address = location.get("address_0")
            if "address_1" in location:
                street_address = location["address_1"]

            phone = "<MISSING>"
            if "phone_md" in location:
                phone = location["phone_md"]
            elif "phone" in location:
                phone = location["phone"]

            hours_of_operation = "<MISSING>"
            if "hours_md" in location:
                hours_of_operation = location["hours_md"]
            elif "hours" in location:
                hours_of_operation = location["hours"]

            yield SgRecord(
                store_number=location["store_number"],
                page_url=location.get("url"),
                location_name=location["name"],
                street_address=street_address,
                city=location["city"],
                state=location["state"],
                zip_postal=location["postal_code"],
                country_code="US",
                phone=phone,
                latitude=location["latitude"],
                longitude=location["longitude"],
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
