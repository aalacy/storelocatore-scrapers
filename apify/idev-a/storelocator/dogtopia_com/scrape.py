from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.dogtopia.com"
    base_url = "https://www.dogtopia.com/wp-json/store-locator/v1/locations.json"
    with SgRequests() as session:
        store_list = session.get(base_url, headers=_headers).json()
        for store in store_list:
            if store["opening_soon"]:
                continue

            addr = store["store_info"]["location_address_info"][0]
            hours = []
            if store["store_info"]["location_hours_info"]:
                _hr = store["store_info"]["location_hours_info"][0]
                if "Opening Soon" in _hr.get("coming_soon_header_text", ""):
                    continue
                times = f"{_hr['monday_open']}-{_hr['monday_close']}"
                if times.strip() == "-":
                    times = "closed"
                hours.append(f"Mon: {times}")
                times = f"{_hr['tuesday_open']}-{_hr['tuesday_close']}"
                if times.strip() == "-":
                    times = "closed"
                hours.append(f"Tue: {times}")
                times = f"{_hr['wednesday_open']}-{_hr['wednesday_close']}"
                if times.strip() == "-":
                    times = "closed"
                hours.append(f"Wed: {times}")
                times = f"{_hr['thursday_open']}-{_hr['thursday_close']}"
                if times.strip() == "-":
                    times = "closed"
                hours.append(f"Thu: {times}")
                times = f"{_hr['friday_open']}-{_hr['friday_close']}"
                if times.strip() == "-":
                    times = "closed"
                hours.append(f"Fri: {times}")
                if "saturday_open" in _hr and "saturday_close" in _hr:
                    times = f"{_hr['saturday_open']}-{_hr['saturday_close']}"
                    if times.strip() == "-":
                        times = "closed"
                    hours.append(f"Sat: {times}")
                if "sunday_open" in _hr and "sunday_close" in _hr:
                    times = f"{_hr['sunday_open']}-{_hr['sunday_close']}"
                    if times.strip() == "-":
                        times = "closed"
                    hours.append(f"Sun: {times}")
            yield SgRecord(
                page_url=store["link"],
                store_number=addr["location_id"],
                location_name=store["title"]["raw"],
                street_address=addr["location_street_address"]
                .replace(",", " ")
                .strip(),
                city=addr["location_city"],
                state=addr["location_state_prov"],
                latitude=addr["location_coordinates"]["latitude"],
                longitude=addr["location_coordinates"]["longitude"],
                zip_postal=addr["location_zip_postal"],
                country_code=addr["location_country"],
                locator_domain=locator_domain,
                phone=addr["location_phone"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
