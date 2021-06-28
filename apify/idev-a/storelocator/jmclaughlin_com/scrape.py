from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "referer": "https://orders.jmclaughlin.com/stores-map?platformType=embedded",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.jmclaughlin.com/"


def publishData(_):
    hours = [f"Mon: {_['Mon']}"]
    hours += [f"Tues: {_['Tues']}"]
    hours += [f"Wed: {_['Wed']}"]
    hours += [f"Thurs: {_['Thurs']}"]
    hours += [f"Fri: {_['Fri']}"]
    hours += [f"Sat: {_['Sat']}"]
    hours += [f"Sun: {_['Sun']}"]
    page_url = f"https://www.jmclaughlin.com/store-details?store={_['StoreIdentifier']['CountryUrl']}/{_['StoreIdentifier']['StateUrl']}/{_['StoreIdentifier']['CityUrl']}/{_['StoreIdentifier']['Address1Url']}/{_['StoreIdentifier']['SupplierNameUrl']}&platformType=embedded"
    return SgRecord(
        page_url=page_url,
        location_name=_["SupplierName"],
        street_address=f"{_['Address1']} {_['Address2']}",
        city=_["City"],
        state=_["State"],
        zip_postal=_["Postcode"],
        country_code=_["Country"],
        phone=_["Phone"],
        latitude=_["MetaData"]["Geometry"]["location"]["lat"],
        longitude=_["MetaData"]["Geometry"]["location"]["lng"],
        location_type=_["MetaData"]["Geometry"]["location_type"],
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
    )


def fetch_data():
    base_url = "https://orders.jmclaughlin.com/states-by-country/US"
    with SgRequests() as session:
        states = session.get(base_url, headers=_headers).json()
        for state in states:
            state_url = (
                f"https://orders.jmclaughlin.com/cities-by-country-state/US/{state}"
            )
            cities = session.get(state_url, headers=_headers).json()
            for city in cities:
                city_url = f"https://orders.jmclaughlin.com/stores-by-country-state-city/US/{state}/{city.replace(' ', '-').replace('.', '-')}"
                locations = session.get(city_url, headers=_headers).json()
                if type(locations) == list:
                    for _ in locations:
                        yield publishData(_)
                else:
                    for id, _ in locations.items():
                        yield publishData(_)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
