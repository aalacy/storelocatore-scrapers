from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://www.toyota.com.cy/api/dealer/drive/34.078641056678606/35.36332843131831?count=2000",
        "https://www.toyota.cz/api/dealer/drive/34.078641056678606/35.36332843131831?count=2000",
        "https://www.toyota.hu/api/dealer/drive/19.042863/47.511472?count=2000&extraCountries=&isCurrentLocation=false",
        "https://www.toyota.ie/api/dealer/drive/19.042863/47.511472?count=2000&extraCountries=&isCurrentLocation=false",
        "https://www.toyota.it/api/dealer/drive/9.182142/45.49352?count=500&extraCountries=&isCurrentLocation=false",
        "https://www.toyota.lv/api/dealer/drive/19.042863/47.511472?count=2000&extraCountries=&isCurrentLocation=false",
        "https://www.toyota.lt/api/dealer/drive/25.274958/54.694969?count=2000&extraCountries=&isCurrentLocation=false",
        "https://www.toyota.pl/api/dealer/drive/19.95/50.06667?count=2000&extraCountries=&isCurrentLocation=false",
        "https://www.toyota.pt/api/dealer/drive/-8.6108/41.1495?count=2000&extraCountries=&isCurrentLocation=false",
        "https://www.toyota.ru/api/dealer/drive/37.4121287410622/55.9698601178023?count=2000&extraCountries=by&isCurrentLocation=false",
        "https://www.toyota.com.tr/api/dealer/drive/30.68333/36.9?count=2000&extraCountries=&isCurrentLocation=false",
        "https://www.toyota.ru/api/dealer/drive/37.61778/55.75583?count=2000&extraCountries=by&isCurrentLocation=false",
    ]
    domain = "toyota.co.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        data = session.get(start_url, headers=hdr).json()
        for poi in data["dealers"]:
            hoo = []
            if poi["openingDays"]:
                all_hours = [
                    e
                    for e in poi["openingDays"]
                    if e["originalService"] == "ShowRoom" and e["hours"]
                ]
                for h in all_hours:
                    start_day = h["startDayCode"]
                    end_day = h["endDayCode"]
                    start_hours = h["hours"][0]["startTime"]
                    end_hours = h["hours"][0]["endTime"]
                    hoo.append(f"{start_day} - {end_day}: {start_hours} - {end_hours}")

            hoo = " ".join(hoo).replace("SAT - SAT", "SAT").replace("SUN - SUN", "SUN")
            street_address = (
                poi["address"]["address1"].strip().split("/İST")[0].split(" Tekirda")[0]
            )
            city = poi["address"]["city"].strip()
            if street_address.lower().endswith(city.lower()):
                street_address = street_address[: -len(city)].replace("/", "").strip()
            zip_code = poi["address"]["zip"]
            if zip_code and "," in zip_code:
                zip_code = ""
            if zip_code and poi["country"] == "ie":
                zip_code = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["url"],
                location_name=poi["name"],
                street_address=street_address,
                city=city,
                state=poi["address"]["region"],
                zip_postal=zip_code,
                country_code=poi["country"],
                store_number=poi.get("localDealerID"),
                phone=poi["phone"],
                location_type="",
                latitude=poi["address"]["geo"]["lat"],
                longitude=poi["address"]["geo"]["lon"],
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
