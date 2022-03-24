from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    params = {
        "AFRICA_EN": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=africa_en&distanceUnit=6371&latitude=-1.2857354&longitude=36.82285630000001&nRadius=10&shopTypeList=E",
        "AFRICA_FR": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=africa_fr&distanceUnit=6371&latitude=-1.2857354&longitude=36.82285630000001&nRadius=10&shopTypeList=E",
        "AL": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=al&distanceUnit=6371&latitude=41.327953&longitude=19.819025&nRadius=10&shopTypeList=E",
        "AR": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=ar&distanceUnit=6371&latitude=-34.603541&longitude=-58.381691&nRadius=10&shopTypeList=E",
        "BE": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=be&distanceUnit=6371&latitude=50.852049&longitude=4.348954&nRadius=10&shopTypeList=E",
        "BG": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=bg&distanceUnit=6371&latitude=42.134892&longitude=24.745681&nRadius=10&shopTypeList=E",
        "CL": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=cl&distanceUnit=6371&latitude=-33.461234&longitude=-70.64209&nRadius=10&shopTypeList=E",
        "CO": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=co&distanceUnit=6371&latitude=4.612016&longitude=-74.078064&nRadius=10&shopTypeList=E",
        "DE": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=de&distanceUnit=6371&latitude=52.519451&longitude=13.403483&nRadius=10&shopTypeList=E",
        "EG": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=eg&distanceUnit=6371&latitude=30.045322&longitude=31.235847&nRadius=10&shopTypeList=E",
        "ES": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=es&distanceUnit=6371&latitude=40.411430&longitude=-3.705629&nRadius=10&shopTypeList=E",
        "GR": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=gr&distanceUnit=6371&latitude=37.983599&longitude=23.729241&nRadius=10&shopTypeList=E",
        "HK_EN": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=hk_en&distanceUnit=6371&latitude=22.280519&longitude=114.158764&nRadius=10&shopTypeList=E",
        "HR": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=hr&distanceUnit=6371&latitude=45.813282&longitude=15.982184&nRadius=10&shopTypeList=E",
        "ID": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=id&distanceUnit=6371&latitude=-6.207456&longitude=106.845474&nRadius=10&shopTypeList=E",
        "IL": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=il&distanceUnit=6371&latitude=31.76904&longitude=35.213585&nRadius=10&shopTypeList=E",
        "IN": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=in&distanceUnit=6371&latitude=28.638773&longitude=77.2229&nRadius=10&shopTypeList=E",
        "IRAN": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=iran&distanceUnit=6371&latitude=35.698571&longitude=51.422882&nRadius=50&shopTypeList=E",
        "IT": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=it&distanceUnit=6371&latitude=41.875569&longitude=12.481066&nRadius=10&shopTypeList=E",
        "LATIN": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=latin&distanceUnit=6371&latitude=8.983321&longitude=-79.51664&nRadius=10&shopTypeList=E",
        "MM": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=mm&distanceUnit=3959&latitude=16.851591&longitude=96.129132&nRadius=10&shopTypeList=E",
        "MX": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=mx&distanceUnit=6371&latitude=19.434219&longitude=-99.135132&nRadius=10&shopTypeList=E",
        "MY": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=my&distanceUnit=6371&latitude=3.144785&longitude=101.684035&nRadius=10&shopTypeList=E",
        "N_AFRICA": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=n_africa&distanceUnit=6371&latitude=33.971979&longitude=-6.849632&nRadius=10&shopTypeList=E",
        "NL": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=nl&distanceUnit=6371&latitude=52.370628&longitude=4.894840&nRadius=10&shopTypeList=E",
        "PE": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=pe&distanceUnit=6371&latitude=-12.0457&longitude=-77.042999&nRadius=10&shopTypeList=E",
        "PH": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=ph&distanceUnit=6371&latitude=14.601026&longitude=120.984192&nRadius=10&shopTypeList=E",
        "PK": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=pk&distanceUnit=6371&latitude=33.731764&longitude=73.093414&nRadius=10&shopTypeList=E",
        "PL": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=pl&distanceUnit=6371&latitude=52.225999&longitude=21.011069&nRadius=10&shopTypeList=E",
        "PT": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=pt&distanceUnit=6371&latitude=38.722147&longitude=-9.139460&nRadius=10&shopTypeList=E",
        "PY": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=py&distanceUnit=6371&latitude=-25.2944175&longitude=-57.5831743&nRadius=10&shopTypeList=E",
        "RO": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=ro&distanceUnit=6371&latitude=44.431084&longitude=26.102191&nRadius=10&shopTypeList=E",
        "RS": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=rs&distanceUnit=6371&latitude=44.818411&longitude=20.460834&nRadius=10&shopTypeList=E",
        "SA_EN": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=sa_en&distanceUnit=6371&latitude=24.654506&longitude=46.713867&nRadius=10&shopTypeList=E",
        "SI": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=si&distanceUnit=6371&latitude=46.049999&longitude=14.500000&nRadius=10&shopTypeList=E",
        "SK": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=sk&distanceUnit=6371&latitude=48.143885&longitude=17.109737&nRadius=10&shopTypeList=E",
        "TR": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=tr&distanceUnit=6371&latitude=39.923429&longitude=32.853241&nRadius=10&shopTypeList=E",
        "TW": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=tw&distanceUnit=6371&latitude=25.090574&longitude=121.558571&nRadius=10&shopTypeList=E",
        "UA": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=ua&distanceUnit=6371&latitude=50.451383&longitude=30.522766&nRadius=10&shopTypeList=E",
        "UY": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=uy&distanceUnit=6371&latitude=-34.9041644&longitude=-56.181662&nRadius=10&shopTypeList=E",
        "ZA": "https://searchapi.samsung.com/v6/front/b2c/storelocator/list?siteCode=za&distanceUnit=6371&latitude=-33.920572&longitude=18.424072&nRadius=10&shopTypeList=E",
    }

    for c, api in params.items():
        locator_domain = f"https://www.samsung.com/{c.lower()}/"
        page_url = f"https://www.samsung.com/{c.lower()}/storelocator/"
        r = session.get(api, headers=headers)
        js = r.json()["response"]["resultData"]["stores"]

        for j in js:
            street_address = j.get("address")
            city = j.get("cityName")
            state = j.get("area")
            postal = j.get("postalCode")
            store_number = j.get("id")
            location_name = j.get("name")
            location_type = j.get("brandType")
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=c,
                latitude=latitude,
                longitude=longitude,
                location_type=location_type,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
