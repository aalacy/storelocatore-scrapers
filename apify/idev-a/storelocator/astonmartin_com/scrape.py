from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

base_url = "https://www.astonmartin.com/api/v1/dealers?latitude=35.6729793&longitude=139.72310400000003&cultureName=en-us&take=2600"


def fetch_data():
    locator_domain = "https://www.astonmartin.com"
    data = []
    with SgRequests() as session:
        locations = session.get(base_url).json()
        for store in locations:
            page_url = (
                locator_domain + store["DealerPageUrl"]
                if store["DealerPageUrl"] is not None
                else "<MISSING>"
            )
            phone = store["PhoneNumber"].strip()
            if phone == "-":
                phone = ""
            is_duplicated = False
            for dd in data:
                if (
                    dd[0] == store["Address"]["Street"]
                    and dd[1] == store["Address"]["Latitude"]
                    and dd[2] == store["Address"]["Longitude"]
                ):
                    is_duplicated = True
            if is_duplicated:
                continue
            data.append(
                [
                    store["Address"]["Street"],
                    store["Address"]["Latitude"],
                    store["Address"]["Longitude"],
                ]
            )
            zip_postal = store["Address"]["Zip"].strip()
            country_code = store["Address"]["CountryCode"]
            if country_code == "United States" and zip_postal:
                zip_postal = zip_postal.split(" ")[-1]
            yield SgRecord(
                page_url=page_url,
                locator_domain=locator_domain,
                location_name=store["Name"],
                street_address=store["Address"]["Street"],
                city=store["Address"]["City"],
                state=store["Address"]["StateCode"],
                zip_postal=zip_postal,
                phone=phone,
                country_code=country_code,
                store_number=store["DCSId"],
                latitude=store["Address"]["Latitude"],
                longitude=store["Address"]["Longitude"],
                hours_of_operation="; ".join(store["OpeningHours"]).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
