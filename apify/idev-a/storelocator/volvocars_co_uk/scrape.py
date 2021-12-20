from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import json

logger = SgLogSetup().get_logger("volvocars")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = " https://volvocars.co.uk/"
urls = {
    "Argentina": "https://www.volvocars.com/ar/dealers/concesionarios",
    "Brazil": "https://www.volvocars.com/br/dealers/concessionarios",
    "Canada": "https://www.volvocars.com/en-ca/dealers/find-retailer",
    "Chile": "https://www.volvocars.com/cl/dealers/concesionarios",
    "Colombia": "https://www.volvocars.com/co/dealers/concesionarios",
    "Mexico": "https://www.volvocars.com/mx/dealers/distribuidores",
    "": "https://www.volvocars.com/za/dealers/find-a-dealer",
    "Australia": "https://www.volvocars.com/au/dealers/find-dealer",
    "India": "https://www.volvocars.com/in/dealers/find-a-dealer",
    "Japan": "https://www.volvocars.com/jp/dealers/dealer-search",
    "Malaysia": "https://www.volvocars.com/my/dealers/find-dealer",
    "Austria": "https://www.volvocars.com/at/dealers/volvo-partner",
    "Belgium": "https://www.volvocars.com/fr-be/dealers/distributeurs",
    "Croatia": "https://www.volvocars.com/hr/dealers/pronadjite-zastupnika",
    "Czech Republic": "https://www.volvocars.com/cz/dealers/najit-prodejce",
    "Denmark": "https://www.volvocars.com/dk/dealers/volvo-forhandlere",
    "Finland": "https://www.volvocars.com/fi/dealers/jalleenmyyjat",
    "France": "https://www.volvocars.com/fr/dealers/concessionnaire",
    "Germany": "https://www.volvocars.com/de/dealers/haendlersuche",
    "Greece": "https://www.volvocars.com/gr/dealers/find-dealer",
    "Hungary": "https://www.volvocars.com/hu/dealers/find-dealer",
    "Ireland": "https://www.volvocars.com/ie/dealers/find-a-dealer",
    "Italy": "https://www.volvocars.com/it/dealers/concessionari",
    "Luxembourg": "https://www.volvocars.com/lu/dealers/distributeurs",
    "Netherlands": "https://www.volvocars.com/nl/dealers/autodealers",
    "Norway": "https://www.volvocars.com/no/dealers/forhandler",
    "Poland": "https://www.volvocars.com/pl/dealers/dealer-volvo",
    "Portugal": "https://www.volvocars.com/pt/dealers/concessionarios",
    "Slovakia": "https://www.volvocars.com/sk/dealers/najdite-predajcu",
    "Slovenia": "https://www.volvocars.com/si/dealers/poiscite-zastopnika",
    "Spain": "https://www.volvocars.com/es/dealers/concesionarios-talleres",
    "Sweden": "https://www.volvocars.com/se/dealers/volvohandlare",
    "Switzerland": "https://www.volvocars.com/fr-ch/dealers/concessionnaires-volvo",
    "Turkey": "https://www.volvocars.com/tr/dealers/yetkili-satici",
    "Ukraine": "https://www.volvocars.com/uk-ua/dealers/find-a-dealer",
    "United Kingdom": "https://www.volvocars.com/uk/dealers/car-retailers",
    "Taiwan": "https://www.volvocars.com/tw/dealers/find-a-dealer",
    "Thailand": "https://www.volvocars.com/en-th/dealers/find-dealer",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            locations = json.loads(
                bs(session.get(base_url, headers=_headers).text, "lxml")
                .select_one("script#__NEXT_DATA__")
                .text
            )["props"]["pageProps"]["retailers"]
            logger.info(f"[{country}] {len(locations)}")
            for _ in locations:
                street_address = city = state = zip_postal = ""
                s_z = _["addressLine2"].split(",")
                zip_postal = s_z[-1]
                if country == "Japan":
                    if len(s_z) == 1:
                        zip_postal = ""
                    state = s_z[0].strip().split()[0]
                    city = s_z[0].strip().split()[1]
                else:
                    city = s_z[0]
                    street_address = _["addressLine1"].replace("\n", " ")

                if country in ["Taiwan", "Japan"]:
                    street_address = _["addressLine1"].split(city)[-1]
                    raw_address = street_address + " " + _["addressLine2"]
                else:
                    street_address = street_address.split(zip_postal)[0]

                if country == "Sweden":
                    zip_postal = " ".join(
                        [zz for zz in zip_postal.split() if zz.isdigit()]
                    )

                raw_address = (
                    street_address + " " + city + " " + state + " " + zip_postal
                )

                phone = ""
                if (
                    _["phoneNumbers"]["retailer"]
                    and _["phoneNumbers"]["retailer"] != "0"
                ):
                    phone = _["phoneNumbers"]["retailer"].split("R")[0].strip()
                elif (
                    _["phoneNumbers"]["service"] and _["phoneNumbers"]["service"] != "0"
                ):
                    phone = _["phoneNumbers"]["service"]
                location_type = []
                for lt in _["capabilities"]:
                    if type(lt) == bool:
                        continue
                    location_type.append(lt)
                yield SgRecord(
                    page_url=_["url"] if _["url"] else base_url,
                    location_name=_["name"].split("(")[0],
                    street_address=street_address,
                    city=city.split("(")[0],
                    state=state,
                    zip_postal=zip_postal,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    location_type=", ".join(location_type),
                    raw_address=raw_address.replace("\n", ""),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
