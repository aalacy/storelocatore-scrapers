from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.canadiantire.ca/"
    base_url = "https://api-triangle.canadiantire.ca/dss/services/v4/stores?lang=en&radius=10000&maxCount=1000&lat=43.653226&lng=-79.3831843&storeType=store"
    with SgRequests() as session:
        locs = session.get(base_url, headers=_headers).json()
        for loc in locs:
            try:
                hours_obj = loc["workingHours"]["general"]
                mon = (
                    "Mon " + hours_obj["monOpenTime"] + "-" + hours_obj["monCloseTime"]
                )
                tue = (
                    " Tue " + hours_obj["tueOpenTime"] + "-" + hours_obj["tueCloseTime"]
                )
                wed = (
                    " Wed " + hours_obj["wedOpenTime"] + "-" + hours_obj["wedCloseTime"]
                )
                thu = (
                    " Thu " + hours_obj["thuOpenTime"] + "-" + hours_obj["thuCloseTime"]
                )
                fri = (
                    " Fri " + hours_obj["friOpenTime"] + "-" + hours_obj["friCloseTime"]
                )
                sat = (
                    " Sat " + hours_obj["satOpenTime"] + "-" + hours_obj["satCloseTime"]
                )
                sun = (
                    " Sun " + hours_obj["sunOpenTime"] + "-" + hours_obj["sunCloseTime"]
                )
                hours_of_operation = mon + tue + wed + thu + fri + sat + sun
            except:
                hours_of_operation = ""

            page_url = f"https://www.canadiantire.ca/en/store-details/{loc['storeProvince']}/{loc['storeCrxNodeName']}.html"

            yield SgRecord(
                page_url=page_url,
                location_name=loc["storeName"],
                store_number=loc["storeNumber"],
                street_address=loc["storeAddress1"] + " " + loc["storeAddress2"],
                state=loc["storeProvince"],
                city=loc["storeCityName"],
                zip_postal=loc["storePostalCode"],
                latitude=loc["storeLatitude"],
                longitude=loc["storeLongitude"],
                location_type=loc["storeType"],
                country_code="CA",
                phone=loc["storeTelephone"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
