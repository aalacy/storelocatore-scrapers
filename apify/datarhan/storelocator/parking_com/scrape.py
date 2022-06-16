import json
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://parking.com/api/parking_lots/all_lot_lat_lng.json?callback=jQuery33101516710439059883_1633074149212"
    domain = "parking.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text.split("49212(")[-1][:-1])
    all_points = data["parkingLots"]
    for point in all_points:
        lat = point["ParkingLot"]["latitude"]
        lng = point["ParkingLot"]["longitude"]
        try:
            data = session.get(
                f"https://parking.com/parking-near/{lat}/{lng}.json", headers=hdr
            ).json()
        except Exception:
            continue
        if not data:
            continue
        for poi in data["lots"]:
            poi_data = session.get(
                f'https://parking.com/lot/{poi["id"]}.json', headers=hdr
            )
            if poi_data.status_code != 200:
                continue
            poi_data = poi_data.json()
            if not poi_data:
                continue
            page_url = urljoin("https://www.parking.com/", poi["url"])
            location_type = "Monthly" if poi["sellsMonthly"] else "Daily"
            city = poi_data["ldjson"][0]["address"]["addressLocality"]
            if not city:
                city = (
                    poi_data["ldjson"][0]["hasMap"]
                    .split("/")[3]
                    .title()
                    .replace("-", " ")
                )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=" ".join(poi["name"].split()),
                street_address=poi_data["ldjson"][0]["address"]["streetAddress"],
                city=city,
                state=poi_data["ldjson"][0]["address"]["addressRegion"],
                zip_postal=poi_data["ldjson"][0]["address"]["postalCode"],
                country_code=poi_data["lot"]["country"],
                store_number=poi["id"],
                phone=poi_data["ldjson"][0]["address"]["telephone"],
                location_type=location_type,
                latitude=poi_data["lot"]["lat"],
                longitude=poi_data["lot"]["lng"],
                hours_of_operation=poi_data["ldjson"][0]["openingHours"],
            )

            yield item


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
