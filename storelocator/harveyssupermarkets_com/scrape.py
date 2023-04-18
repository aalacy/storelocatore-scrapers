from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

locator_domain = "https://www.harveyssupermarkets.com/"
base_url = "https://www.harveyssupermarkets.com/V2/storelocator/getStores?search=jacksonville,%20fl&strDefaultMiles=1000&filter="


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xc3\\xa9", "e")
            .replace("\\xa0", "")
            .replace("\\xa0\\xa", "")
            .replace("\\xae", "")
        )
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        locations = res.json()
        for _ in locations:
            page_url = f"https://www.harveyssupermarkets.com/storedetails?search={_['StoreCode']}&zipcode={_['Address']['Zipcode']}&referby=_sd"
            location_name = f'Harveys at {_["Address"]["AddressLine1"]}'
            if not _["Address"]["AddressLine1"]:
                location_name = f'Harveys at {_["Address"]["AddressLine2"]}'
            yield SgRecord(
                store_number=_["StoreCode"],
                page_url=page_url,
                location_name=location_name,
                street_address=f'{_["Address"]["AddressLine2"]}',
                city=_["Address"]["City"],
                state=_["Address"]["State"],
                zip_postal=_["Address"]["Zipcode"],
                country_code=_["Address"]["Country"],
                phone=_["Phone"],
                latitude=_["Location"]["Latitude"],
                longitude=_["Location"]["Longitude"],
                locator_domain=locator_domain,
                hours_of_operation=_valid1(_["WorkingHours"].replace(",", ";")),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
