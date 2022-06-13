# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://fr.renault.be/wired/commerce/v1/dealers/locator?lat=51.3526098&lon=3.2171343&language=fr&country=be&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue&pageSize=250&count=250",
        "https://fr.renault.ch/wired/commerce/v1/dealers/locator?lat=46.90398737977236&lon=7.87785950809382&country=ch&language=fr&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue%3BbirId!%3D75665070%3BbirId!%3D75665042&count=250",
        "https://www.renault.at/wired/commerce/v1/dealers/locator?lat=47.516231&lon=14.550072&language=de&country=at&filters=renault.blacklisted%3D%3Dfalse&pageSize=100&count=100",
        "https://www.renault.bg/wired/commerce/v1/dealers/locator?lat=42.733883&lon=25.48583&language=bg&country=bg&pageSize=250&count=250",
        "https://www.renault.co.in/wired/commerce/v1/dealers/locator?lat=20.593684&lon=78.96288&language=en&country=in&pageSize=250&count=250",
        "https://www.renault.com.ar/wired/commerce/v1/dealers/locator?lat=-38.416097&lon=-63.61667199999999&language=es&country=ar&filters=renault.blacklisted%3D%3Dfalse%3B(activities%3D%3D01+or+activities%3D%3D04+or+activities%3D%3D08)&pageSize=250&count=250",
        "https://www.renault.com.br/wired/commerce/v1/dealers/locator?lat=-14.235004&lon=-51.92528&language=pt&country=br&filters=activities%3D%3D01&pageSize=250&count=250",
        "https://www.renault.com.co/wired/commerce/v1/dealers/locator?lat=3.7508979&lon=-76.23358720000002&language=es&country=co&pageSize=250&count=250",
        "https://www.renault.com.mx/wired/commerce/v1/dealers/locator?lat=19.4326077&lon=-99.133208&language=es&country=mx&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue&pageSize=200&count=200",
        "https://www.renault.com.tr/wired/commerce/v1/dealers/locator?lat=39.83914950316404&lon=32.8077009474591&country=tr&language=tr&count=500",
        "https://www.renault.cz/wired/commerce/v1/dealers/locator?lat=49.63240646868809&lon=11.437971914062501&country=cz&language=cs&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue&count=250",
        "https://www.renault.dz/wired/commerce/v1/dealers/locator?lat=37.593429028061394&lon=0.7801122745940461&country=dz&language=fr&count=250",
        "https://www.renault.es/wired/commerce/v1/dealers/locator?lat=42.52332520528748&lon=0.5165877363631921&country=es&language=es&filters=renault.blacklisted%3D%3Dfalse%3BbirId!%3D72405033%3BbirId!%3D72405300%3BbirId!%3D72405030&count=350",
        "https://www.renault.hr/wired/commerce/v1/dealers/locator?lat=45.0533884&lon=18.749194&language=hr&country=hr&pageSize=250&count=250",
        "https://www.renault.hr/wired/commerce/v1/dealers/locator?lat=45.1&lon=15.2&language=hr&country=hr&pageSize=250&count=250",
        "https://www.renault.hr/wired/commerce/v1/dealers/locator?lat=45.235865617062586&lon=12.899979665624983&country=hr&language=hr&count=250",
        "https://www.renault.hu/wired/commerce/v1/dealers/locator?lat=47.024817328327&lon=18.713377522426697&country=hu&language=hu&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue%3BbirId!%3D34810186&count=250",
        "https://www.renault.ie/wired/commerce/v1/dealers/locator?lat=53.41291&lon=-8.24389&language=en&country=ie&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue&pageSize=100&count=10&renaultChoice=true",
        "https://www.renault.it/wired/commerce/v1/dealers/locator?lat=42.20211903631653&lon=11.024462376720066&country=it&language=it&filters=renault.blacklisted%3D%3Dfalse&count=350",
        "https://www.renault.lu/wired/commerce/v1/dealers/locator?lat=49.73205904507725&lon=6.161050037670634&country=lu&language=fr&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue&count=250",
        "https://www.renault.ma/wired/commerce/v1/dealers/locator?lat=33.655919774976994&lon=-7.761735493164053&country=ma&language=fr&count=250",
        "https://www.renault.nl/wired/commerce/v1/dealers/locator?lat=53.352603851441785&lon=-0.17280033531881145&country=nl&language=nl&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue&count=250",
        "https://www.renault.pl/wired/commerce/v1/dealers/locator?lat=52.96897229986192&lon=18.97114638818732&country=pl&language=pl&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue%3BbirId!%3D61617151&count=250",
        "https://www.renault.pt/wired/commerce/v1/dealers/locator?lat=39.94890738234113&lon=-8.673031797556433&country=pt&language=pt&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue&count=100",
        "https://www.renault.ro/wired/commerce/v1/dealers/locator?lat=45.697606536806745&lon=23.72748063242625&country=ro&language=ro&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue%3BbirID!%3D64200027%3BbirId!%3D64200279&count=250",
        "https://www.renault.rs/wired/commerce/v1/dealers/locator?lat=46.53406439633622&lon=19.53827759820561&country=rs&language=sr&count=250",
        "https://www.renault.ru/wired/commerce/v1/dealers/locator?lat=56.46543519999999&lon=37.5699891&language=ru&country=ru&filters=renault.blacklisted%3D%3Dfalse&pageSize=200&count=200",
        "https://www.renault.sk/wired/commerce/v1/dealers/locator?lat=48.669026&lon=19.699024&language=sk&country=sk&filters=renault.blacklisted%3D%3Dfalse%3Brenault.receiveLead%3D%3Dtrue&pageSize=250&count=250",
        "https://www.renault.ua/wired/commerce/v1/dealers/locator?lat=48.379433&lon=31.16558&language=uk&country=ua&filters=deliveryDistribution%3D%3Dfalse&pageSize=250&count=250",
    ]
    page_urls = {
        "www.renault.com.ar": "https://www.renault.com.ar/concesionarios.html",
        "fr.renault.be": "https://fr.renault.be/trouvez-votre-concessionnaire.html",
        "fr.renault.ch": "https://fr.renault.ch/concessionnaires.html",
        "www.renault.at": "https://www.renault.at/haendlersuche.html",
        "www.renault.bg": "https://www.renault.bg/namerete-dilarstvo.html",
        "www.renault.co.in": "https://www.renault.co.in/find-a-dealer.html",
        "renault.com.ar": "https://www.renault.com.ar/concesionarios.html",
        "www.renault.com.br": "https://www.renault.com.br/encontre-uma-concessionaria.html",
        "www.renault.com.co": "https://www.renault.com.co/concesionarios.html",
        "www.renault.com.mx": "https://www.renault.com.mx/encuentra-una-agencia.html",
        "renault.com.tr": "https://www.renault.com.tr/yetkili-satici-bul.html",
        "renault.cz": "https://www.renault.cz/najit-dealera.html",
        "www.renault.dz": "https://www.renault.dz/trouver-un-distributeur.html",
        "www.renault.es": "https://www.renault.es/concesionarios.html",
        "www.renault.hr": "https://www.renault.hr/koncesionari.html",
        "www.renault.hu": "https://www.renault.hu/kereskedes-keresese.html",
        "www.renault.ie": "https://www.renault.ie/find-a-dealer.html",
        "www.renault.it": "https://www.renault.it/rete-renault.html",
        "www.renault.lu": "https://www.renault.lu/trouvez-votre-concessionnaire.html",
        "www.renault.ma": "https://www.renault.ma/trouvez-un-concessionnaire.html",
        "www.renault.nl": "https://www.renault.nl/dealers.html",
        "www.renault.pl": "https://www.renault.pl/znajdz-dealera.html",
        "www.renault.pt": "https://www.renault.pt/concessionarios.html",
        "www.renault.ro": "https://www.renault.ro/reteaua-renault.html",
        "www.renault.rs": "https://www.renault.rs/distributeri.html",
        "www.renault.ru": "https://www.renault.ru/find-a-dealer.html",
        "www.renault.sk": "https://www.renault.sk/najst-dealera.html",
        "www.renault.ua": "https://www.renault.ua/find-a-dealer.html",
        "www.renault.com.tr": "https://www.renault.com.tr/yetkili-satici-bul.html",
        "www.renault.cz": "https://www.renault.cz/najit-dealera.html",
    }
    domain = "renault.be"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        all_locations = session.get(start_url, headers=hdr).json()
        for poi in all_locations:
            zip_code = poi.get("postalCode")
            if zip_code and zip_code in ["00000", "Mayo", "EIRE", "0"]:
                zip_code = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_urls[start_url.split("/")[2]],
                location_name=poi["name"],
                street_address=poi["streetAddress"],
                city=poi["locality"],
                state="",
                zip_postal=zip_code,
                country_code=poi["country"],
                store_number=poi["dealerId"],
                phone=poi["telephone"].get("value"),
                location_type=poi["type"],
                latitude=poi.get("geolocalization", {}).get("lat"),
                longitude=poi.get("geolocalization", {}).get("lon"),
                hours_of_operation="",
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
