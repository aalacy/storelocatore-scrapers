from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests


def fetch_data():
    locator_domain = "https://www.cotswoldoutdoor.com"
    base_url = "https://www.cotswoldoutdoor.com/api/services/public/store/cotswold/en"
    with SgRequests() as session:
        store_list = session.get(base_url).json()
        for store in store_list:
            page_url = (
                "https://www.cotswoldoutdoor.com/stores/" + store["alias"] + ".html"
            )
            if store["country"] != "GB":
                continue
            hours = []
            for x in store["dailyOpeningHours"][0]:
                hours.append(
                    x["day"]
                    + ": "
                    + (
                        "Closed"
                        if x["open"] == 0
                        else str(x["openTimeLabel"])
                        + "-"
                        + str(x["closeTimeInMinutes"])
                    )
                )

            yield SgRecord(
                page_url=page_url,
                location_name=store["name"],
                store_number=store["code"],
                street_address=store["street"],
                city=store["city"],
                zip_postal=store["postalcode"],
                phone=store["phoneNumber"],
                locator_domain=locator_domain,
                latitude=store["latitude"],
                longitude=store["longitude"],
                country_code=store["country"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
