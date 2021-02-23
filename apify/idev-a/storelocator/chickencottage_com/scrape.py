from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

locator_domain = "https://chickencottage.com"


def fetch_data():
    with SgRequests() as session:
        res = session.post(
            "https://chickencottage.com/restaurants/?/front/get/53.8337367/-2.4290148/1"
        )
        store_list = json.loads(res.text)
        for store in store_list:
            location_name = store["name"]
            store_number = store["id"]
            latitude = store["lat"]
            longitude = store["lng"]
            detail = bs(store["display"], "lxml")
            address_detail = detail.select_one("li.lpr-location-address").contents
            address_detail = [x for x in address_detail if x.string is not None]
            country_code = "UK"
            except_ids = ["124", "125", "126"]
            if store_number == "1":
                state = "<MISSING>"
                address_detail = address_detail[:-1]
            elif store_number in except_ids:
                state = "<MISSING>"
                city_zip = address_detail.pop()
                city = " ".join(city_zip.split(" ")[:-2])
                zip = " ".join(city_zip.split(" ")[-2:])
            else:
                address_detail = address_detail[:-1]
                state = address_detail.pop()
            address_detail = address_detail[0].split(",")
            if store_number not in except_ids:
                zip = address_detail.pop()
                if " Scotland" in address_detail:
                    state = address_detail.pop()
                city = address_detail.pop()
            street_address = ",".join(address_detail)
            page_url = "https://chickencottage.com/restaurants/"
            phone = detail.select_one("li.lpr-location-phone")
            phone = (
                phone.text.replace("Phone: ", "") if phone is not None else "<MISSING>"
            )
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip,
                state=state,
                phone=phone,
                locator_domain=locator_domain,
                country_code=country_code,
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
