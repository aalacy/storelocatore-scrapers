from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

locator_domain = "https://www.russellandbromley.co.uk"


def fetch_data():
    with SgRequests() as session:
        res = session.get(
            "https://www.russellandbromley.co.uk/ccstoreui/v1/search?Nfg=Store.geocode%7C53.4807593%7C-2.2426305%7C804.672&Ns=Store.geocode(53.4807593%2C-2.2426305)&Ntk=Store&Nr=AND(record.type%3AStore)&No=0&Nrpp=250"
        )
        store_list = json.loads(res.text)["resultsList"]["records"]
        for store in store_list:
            store = store["records"][0]
            location_name = store["attributes"]["Store.storeName"][0]
            store_number = store["attributes"]["Store.storeNumber"][0]
            latitude = store["attributes"]["Store.geocode"][0].split(",")[0]
            longitude = store["attributes"]["Store.geocode"][0].split(",")[1]
            zip = store["attributes"]["Store.postCode"][0]
            city = store["attributes"]["Store.city"][0]
            country_code = "UK"
            street_address = store["attributes"]["Store.addressLine1"][0] + " "
            street_address += (
                store["attributes"]["Store.addressLine2"][0]
                if "Store.addressLine2" in store["attributes"]
                else ""
            )
            hours_of_operation = store["attributes"]["Store.openingHours"][0]
            location_type = (
                store["attributes"]["Store.store.type"][0]
                if "Store.store.type" in store["attributes"]
                else "<MISSING>"
            )
            phone = store["attributes"]["Store.telephone"][0]
            page_url = locator_domain + store["attributes"]["product.route"][0]
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city,
                zip_postal=zip,
                phone=phone,
                locator_domain=locator_domain,
                country_code=country_code,
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                location_type=location_type,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
