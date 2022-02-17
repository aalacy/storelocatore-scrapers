from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

base_url = "https://arthurmurray.com/assets/data/locations.json"
domain = "arthurmurray.com"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        for poi in session.get(base_url).json():
            page_url = "https://arthurmurray.com/locations/" + poi["slug"]
            street_address = poi["address"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]

            hours_of_operation = poi["hours1"].replace("&#44;", " ")
            if hours_of_operation and poi["name"] == "Arthur Murray Zurich":
                times = []
                dd = []
                for hh in hours_of_operation.split("  "):
                    if not hh.strip():
                        continue
                    if hh.startswith("-"):
                        dd[-1] += hh
                    elif hh.split()[-1] in days:
                        dd.append(hh)
                    else:
                        times.append(hh.replace("clock", "").strip())

                hours = []
                for x in range(len(dd)):
                    hours.append(f"{dd[x]}: {times[x]}")
                hours_of_operation = "; ".join(hours)
            yield SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["postal"],
                country_code=poi["country"],
                store_number="",
                phone=poi["phone"],
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lng"],
                hours_of_operation=hours_of_operation,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
