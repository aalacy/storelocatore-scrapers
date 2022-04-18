from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = {
        "Croatia": "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/lexus/hr/hr/drive/16.059354/45.732163?count=500&extraCountries=UK&limitSearchDistance=0&isCurrentLocation=false&services=",
        "Bulgaria": "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/lexus/bg/bg/drive/23.350282/42.652363?count=500&extraCountries=UK&limitSearchDistance=0&isCurrentLocation=false&services=",
        "Switzerland": "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/lexus/ch/de/drive/8.53989/47.378084?count=500&extraCountries=&isCurrentLocation=false",
        "Spain": "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/lexus/es/es/drive/-3.703583/40.416705?count=500&extraCountries=&isCurrentLocation=false",
        "France": "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/lexus/fr/fr/drive/0.428551/44.064432?count=500&extraCountries=AD|MC&isCurrentLocation=false",
        "Estonia": "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/lexus/ee/et/drive/24.745369/59.437216?count=500&extraCountries=&isCurrentLocation=false",
    }
    page_url = {
        "hr": "https://www.lexus.hr/contact/dealers",
        "bg": "https://www.lexus.bg/contact/dealers",
        "ch": "https://de.lexus.ch/#/publish/my_lexus_my_dealers",
        "es": "https://www.lexusauto.es/#/publish/my_lexus_my_dealers",
        "fr": "https://www.lexus.fr/#/publish/my_lexus_my_dealers",
        "ee": "https://ee.lexus.ee/#/publish/my_lexus_my_dealers",
    }

    domain = "lexus.hr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for country_code, start_url in start_urls.items():
        data = session.get(start_url, headers=hdr).json()
        for poi in data["dealers"]:
            country_code = poi["country"]
            hoo = ""
            if poi.get("openingDays"):
                hoo = []
                if poi["openingDays"][0]["originalService"] == "ShowRoom":
                    start_day = poi["openingDays"][0]["startDayCode"]
                    end_day = poi["openingDays"][0]["endDayCode"]
                    opens = poi["openingDays"][0]["hours"][0]["startTime"]
                    closed = poi["openingDays"][0]["hours"][0]["endTime"]
                    hoo.append(f"{start_day} - {end_day}: {opens} - {closed}")
                hoo = " ".join(hoo)
            location_type = []
            for e in poi["services"]:
                location_type.append(e["label"])
            location_type = ", ".join(location_type)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url[country_code],
                location_name=poi["name"],
                street_address=poi["address"]["address1"],
                city=poi["address"]["city"],
                state=poi["address"]["region"],
                zip_postal=poi["address"]["zip"],
                country_code=country_code,
                store_number="",
                phone=poi["phone"],
                location_type=location_type,
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
