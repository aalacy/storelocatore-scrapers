from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.dunelondon.com"


def fetch_data():
    with SgRequests() as session:
        base_url = "https://www.dunelondon.com/rw/stores/?validate=0&longitude=0&lattitude=0&dummyInput=&countryChoice=UK&sl_postcode="
        res = session.get(base_url)
        store_list = json.loads(
            res.text.split("var myStores = ")[1].split(";</script>")[0]
        )["stores"]
        for store in store_list:
            if store["country"] == "IE":
                continue
            page_url = store["storeLink"]
            location_name = store["name"]
            zip = store["postcode"].strip()
            city = store["town"]
            street_address = store["address1"]
            country_code = store["country"]
            phone = store["storecontacts"]
            store_number = store["storenumber"]
            latitude = store["pca_wgs84_latitude"]
            longitude = store["pca_wgs84_longitude"]
            location_type = store["storeType"]
            hours = bs(store["openinghours"], "lxml").select_one("p").contents
            hours = [x for x in hours if x.string is not None]
            hours_of_operation = " ".join(hours)
            if latitude == "" or latitude is None:
                res = session.get(page_url)
                latitude = res.text.split("var pca_default_position_lat = '")[1].split(
                    "'"
                )[0]
                longitude = res.text.split("var pca_default_position_long = '")[
                    1
                ].split("'")[0]

            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip,
                phone=phone,
                store_number=store_number,
                country_code=country_code,
                locator_domain=locator_domain,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
