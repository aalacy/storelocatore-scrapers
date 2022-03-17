from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = {
        "UK": "https://www.lexus.co.uk/api/dealers/all",
        "Austria": "https://www.lexus.at/api/dealers/all",
        "Belgium": "https://fr.lexus.be/api/dealers/all",
        "Estonia": "https://ee.lexus.ee/api/dealers/all",
        "France": "https://www.lexus.fr/api/dealers/all",
        "Germany": "https://www.lexus.de/api/dealers/all",
        "Hungary": "https://www.lexus.hu/api/dealers/all",
        "Italy": "https://www.lexus.it/api/dealers/all",
        "Latvia": "https://lv.lexus.lv/api/dealers/all",
        "Lithuania": "https://lt.lexus.lt/api/dealers/all",
        "Luxembourg": "https://www.lexus.lu/api/dealers/all",
        "Netherlands": "https://www.lexus.nl/api/dealers/all",
        "Poland": "https://www.lexus-polska.pl/api/dealers/all",
        "Portugal": "https://www.lexus.pt/api/dealers/all",
        "Sweden": "https://www.lexus.se/api/dealers/all",
        "Ukrain": "https://www.lexus.ua/api/dealers/all",
        "Spain": "https://www.lexusauto.es/api/dealers/all",
    }

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for country, start_url in start_urls.items():
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
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=start_url.split("/")[2].replace("www.", ""),
                page_url=poi.get("url"),
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
