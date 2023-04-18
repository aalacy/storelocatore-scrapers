from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json; charset=utf-8",
    "origin": "https://www.jeancoutu.com",
    "referer": "https://www.jeancoutu.com/localisateur-succursale/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
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


def _time(time):
    return time[:2] + ":" + time[2:]


days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.jeancoutu.com/"
        base_url = (
            "https://www.jeancoutu.com/StoreLocator/StoreLocator.svc/LoadStoreInfosBH"
        )
        locations = session.post(base_url, headers=_headers).json()
        for _ in locations["LoadStoreInfosBHResult"]:
            hours = []
            for hour in _["StoreBusinessHours"]:
                time = f"{_time(hour['OpenTime'])}-{_time(hour['CloseTime'])}"
                if hour["ClosedAllDay"]:
                    time = "Closed"
                hours.append(f"{days[int(hour['Day'])-1]}: {time}")
            yield SgRecord(
                page_url=f"https://www.jeancoutu.com/localisateur-succursale/{_['Store']}/",
                store_number=_["Store"],
                location_name=_["Store_Name"],
                street_address=_["Address_e"],
                city=_["City"],
                zip_postal=_["Zip_Code"],
                country_code="CA",
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                phone=_["Front_Phone"],
                location_type=_["StoreType"],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
