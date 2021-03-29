from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "referer": "https://orders.jmclaughlin.com/stores-map?platformType=embedded",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

data = {
    "supplierIds": "10,11,12,13,15,17,18,22,23,25,27,29,30,31,32,34,35,36,37,38,39,40,41,42,43,44,45,48,50,51,52,53,54,56,61,62,63,66,72,73,74,79,80,83,86,87,89,93,101,103,104,105,106,107,108,110,111,112,113,114,115,116,117,118,119,120,122,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,215"
}


def fetch_data():
    locator_domain = "https://www.jmclaughlin.com/"
    base_url = "https://orders.jmclaughlin.com/loadStoresBySupplierIds"
    with SgRequests() as session:
        locations = json.loads(
            session.post(base_url, headers=_headers, data=data).text.replace(
                '\\"', '"'
            )[1:-1]
        )
        for id, _ in locations.items():
            hours = [f"Mon: {_['Mon']}"]
            hours += [f"Tues: {_['Tues']}"]
            hours += [f"Wed: {_['Wed']}"]
            hours += [f"Thurs: {_['Thurs']}"]
            hours += [f"Fri: {_['Fri']}"]
            hours += [f"Sat: {_['Sat']}"]
            hours += [f"Sun: {_['Sun']}"]
            page_url = f"https://www.jmclaughlin.com/store-details?store={_['StoreIdentifier']['CountryUrl']}/{_['StoreIdentifier']['StateUrl']}/{_['StoreIdentifier']['CityUrl']}/{_['StoreIdentifier']['Address1Url']}/{_['StoreIdentifier']['SupplierNameUrl']}&platformType=embedded"
            yield SgRecord(
                page_url=page_url,
                store_number=id,
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


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
