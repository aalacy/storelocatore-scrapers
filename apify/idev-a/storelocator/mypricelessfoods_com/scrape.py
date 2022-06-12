from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from datetime import timezone, datetime


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xa0", "")
            .replace("\\xa0\\xa", "")
            .replace("\\xae", "")
        )
    else:
        return ""


_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.mypricelessfoods.com",
    "referer": "https://www.mypricelessfoods.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.mypricelessfoods.com/"
        session_url = "https://api.freshop.com/2/sessions/create"
        form_data = {
            "app_key": "priceless",
            "referrer": "https://www.mypricelessfoods.com/my-store/store-locator",
            "utc": str(datetime.now().replace(tzinfo=timezone.utc).timestamp()),
        }
        res = session.post(session_url, data=form_data, headers=_headers).json()
        res = session.get(
            f"https://api.freshop.com/1/stores?app_key=priceless&has_address=true&limit=-1&token={res['token']}",
        )
        store_list = res.json()["items"]

        for store in store_list:
            store_number = store["store_number"]
            city = store["city"]
            state = store["state"]
            page_url = store["url"] if "url" in store.keys() else "<MISSING>"
            hours_of_operation = (
                store["hours_md"] if "hours_md" in store.keys() else "<MISSING>"
            )
            location_name = store["name"]
            street_address = (
                store["address_1"]
                if "address_1" in store.keys()
                else (
                    store["address_0"] if "address_0" in store.keys() else "<MISSING>"
                )
            )
            zip = store["postal_code"]
            country_code = (
                store["country"] if "country" in store.keys() else "<MISSING>"
            )
            phone = store["phone"] if "phone" in store.keys() else "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]

            yield SgRecord(
                store_number=store_number,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=_valid1(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
