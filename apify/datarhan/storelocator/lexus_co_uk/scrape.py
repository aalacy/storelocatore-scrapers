from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://www.lexus.hu/api/dealers/all",
        "https://lv.lexus.lv/api/dealers/all",
        "https://www.lexus-polska.pl/api/dealers/all",
    ]

    loc_url = {
        "hu": "https://www.lexus.hu/",
        "lv": "https://lv.lexus.lv/",
        "pl": "https://www.lexus-polska.pl/",
    }

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        data = session.get(start_url, headers=hdr).json()
        for poi in data["dealers"]:
            location_type = ", ".join(poi["services"])
            if "ShowRoom" not in location_type:
                continue
            if not poi["address"]:
                continue
            street_address = poi["address"]["address1"]
            if poi["address"].get("address"):
                street_address += ", " + poi["address"]["address"]
            street_address = street_address.replace("&#xD;&#xA;", " ")
            hoo = []
            if poi["openingTimes"].get("ShowRoom"):
                for e in poi["openingTimes"]["ShowRoom"]:
                    hours = []
                    for h in e["slots"]:
                        hours.append(f'{h["openFrom"]} - {h["openTo"]}')
                    hoo.append(f'{e["day"]}: {", ".join(hours)}')
            hoo = " ".join(hoo).strip()
            if hoo.endswith("Sunday:"):
                hoo += " closed"

            item = SgRecord(
                locator_domain=start_url.split("/")[2].replace("www.", ""),
                page_url=loc_url[poi["country"]],
                location_name=poi["name"],
                street_address=street_address,
                city=poi["address"]["city"],
                state=poi["address"]["region"],
                zip_postal=poi["address"]["zip"].replace("LV-", "").replace("LT-", ""),
                country_code=poi["country"],
                store_number="",
                phone=poi["phone"],
                location_type=location_type,
                latitude=poi["address"].get("geo", {}).get("lat"),
                longitude=poi["address"].get("geo", {}).get("lon"),
                hours_of_operation=hoo,
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
