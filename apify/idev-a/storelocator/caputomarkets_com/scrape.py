from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://caputomarkets.com/"
    page_url = "https://caputomarkets.com/shop/guide#modal=zip-check"
    base_url = "https://deliveries.locai.io/locations?clientId=bdaba286-2072-44e2-bf00-e2c13d6c68f7"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            hours = []
            tm = _["store"]["hours"]
            hours.append(f"monday: {tm['monday']['open']}-{tm['monday']['close']}")
            hours.append(f"tuesday: {tm['tuesday']['open']}-{tm['tuesday']['close']}")
            hours.append(
                f"wednesday: {tm['wednesday']['open']}-{tm['wednesday']['close']}"
            )
            hours.append(
                f"thursday: {tm['thursday']['open']}-{tm['thursday']['close']}"
            )
            hours.append(f"friday: {tm['friday']['open']}-{tm['friday']['close']}")
            hours.append(
                f"saturday: {tm['saturday']['open']}-{tm['saturday']['close']}"
            )
            hours.append(f"sunday: {tm['sunday']['open']}-{tm['sunday']['close']}")
            street_address = _["addressLine1"]
            if _["addressLine2"]:
                street_address += " " + _["addressLine2"]
            location_name = _["store"]["name"]
            street_address = street_address.replace(location_name, "").strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_["store"]["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["store"]["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
