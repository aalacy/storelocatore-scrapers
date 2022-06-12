# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_urls = [
        "https://www.dacia.si/wired/commerce/v1/dealers/locator?lat=46.13927081697352&lon=12.43547399765626&country=si&language=sl&count=250",
        "https://de.dacia.ch/wired/commerce/v1/dealers/locator?lat=45.86385620202452&lon=7.188434037746589&country=ch&language=de&filters=dacia.blacklisted%3D%3Dfalse%3Bdacia.receiveLead%3D%3Dtrue%3BbirId!%3D75665070%3BbirId!%3D75665042%3BbirId!%3D75665017%3BbirId!%3D75614224%3BbirId!%3D75611944%3BbirId!%3D75611926%3BbirId!%3D75611948%3BbirId!%3D75602021%3BbirId!%3D75601017%3BbirId!%3D75662664%3BbirId!%3D75663026%3BbirId!%3D75611724%3BbirId!%3D75611935%3BbirId!%3D75601721%3BbirId!%3D75601028%3BbirId!%3D75606825%3BbirId!%3D75601019%3BbirId!%3D75656012%3BbirId!%3D75656015%3BbirId!%3D75665079%3BbirId!%3D75663057%3BbirId!%3D75656021%3BbirId!%3D75665006%3BbirId!%3D75602026%3BbirId!%3D75601021%3BbirId!%3D75601023%3BbirId!%3D75601024%3BbirId!%3D75614526%3BbirId!%3D75663054%3BbirId!%3D75656014%3BbirId!%3D75601031%3BbirId!%3D75663056%3BbirId!%3D75600308%3BbirId!%3D75663024%3BbirId!%3D75663058%3BbirId!%3D75601027%3BbirId!%3D75664553%3BbirId!%3D75601729%3BbirId!%3D75606927%3BbirId!%3D75606840%3BbirId!%3D75614422%3BbirId!%3D75600320%3BbirId!%3D75664803%3BbirId!%3D75614426%3BbirId!%3D75606922%3BbirId!%3D75606926%3BbirId!%3D75601029%3BbirId!%3D75611932&count=250",
        "https://fr.dacia.be/wired/commerce/v1/dealers/locator?lat=51.39537234231864&lon=5.083493042674007&country=be&language=fr&filters=dacia.blacklisted%3D%3Dfalse%3Bdacia.receiveLead%3D%3Dtrue&count=250",
        "https://www.dacia.com.tr/wired/commerce/v1/dealers/locator?lat=39.51822262179962&lon=33.845451003921&country=tr&language=tr&filters=dacia.blacklisted%3D%3Dfalse%3BbirId!%3D79298367&count=250",
        "https://www.dacia.cz/wired/commerce/v1/dealers/locator?lat=49.849244726567576&lon=15.186741146192958&country=cz&language=cs&filters=dacia.blacklisted%3D%3Dfalse%3Bdacia.receiveLead%3D%3Dtrue&count=250",
        "https://www.dacia.de/wired/commerce/v1/dealers/locator?lat=51.22546436342881&lon=10.234832743585827&country=de&language=de&filters=dacia.blacklisted%3D%3Dfalse&count=250",
        "https://www.dacia.dz/wired/commerce/v1/dealers/locator?lat=38.29173559884467&lon=1.6300725071733098&country=dz&language=fr&count=250",
        "https://www.dacia.es/wired/commerce/v1/dealers/locator?lat=40.70437292010806&lon=-1.854018194797817&country=es&language=es&filters=dacia.blacklisted%3D%3Dfalse%3BbirId!%3D72405033%3BbirId!%3D72405300&count=350",
        "https://www.dacia.fr/wired/commerce/v1/dealers/locator?lat=47.69592771699254&lon=2.23975757431063&country=fr&language=fr&filters=dacia.blacklisted%3D%3Dfalse&count=150",
        "https://www.dacia.hr/wired/commerce/v1/dealers/locator?lat=44.29344378116551&lon=15.36316080182479&country=hr&language=hr&count=250",
        "https://www.dacia.hu/wired/commerce/v1/dealers/locator?lat=47.48462790536408&lon=18.70832198194165&country=hu&language=hu&filters=dacia.blacklisted%3D%3Dfalse%3Bdacia.receiveLead%3D%3Dtrue&count=250",
        "https://www.dacia.it/wired/commerce/v1/dealers/locator?lat=41.53452143264448&lon=13.930702173009081&country=it&language=it&filters=dacia.blacklisted%3D%3Dfalse&count=350",
        "https://www.dacia.lu/wired/commerce/v1/dealers/locator?lat=49.534387549855126&lon=7.363778011529945&country=lu&language=fr&filters=dacia.blacklisted%3D%3Dfalse%3Bdacia.receiveLead%3D%3Dtrue&count=250",
        "https://www.dacia.ma/wired/commerce/v1/dealers/locator?lat=33.604636874164726&lon=-7.513856464843741&country=ma&language=fr&count=250",
        "https://www.dacia.nl/wired/commerce/v1/dealers/locator?lat=52.09178578415626&lon=4.35796857347222&country=nl&language=nl&filters=dacia.blacklisted%3D%3Dfalse%3Bdacia.receiveLead%3D%3Dtrue&count=250",
        "https://www.dacia.pl/wired/commerce/v1/dealers/locator?lat=52.19291267474554&lon=20.245607335979912&country=pl&language=pl&filters=dacia.blacklisted%3D%3Dfalse%3Bdacia.receiveLead%3D%3Dtrue%3BbirId!%3D61617948%3BbirId!%3D61617506%3BbirId!%3D61617134%3BbirId!%3D61617949%3BbirId!%3D61617810%3BbirId!%3D61617859%3BbirId!%3D61617118%3BbirId!%3D61617893%3BbirId!%3D61617892%3BbirId!%3D61617020%3BbirId!%3D61617102%3BbirId!%3D61617895%3BbirId!%3D61617881%3BbirId!%3D61617947%3BbirId!%3D61617504%3BbirId!%3D61617945%3BbirId!%3D61617110%3BbirId!%3D61617066%3BbirId!%3D61617800%3BbirId!%3D61617151&count=250",
        "https://www.dacia.ro/wired/commerce/v1/dealers/locator?lat=45.681199386460406&lon=23.959507546139548&country=ro&language=ro&filters=dacia.blacklisted%3D%3Dfalse%3Bdacia.receiveLead%3D%3Dtrue%3BbirId!%3D64200017%3BbirId!%3D64200204%3BbirId!%3D64200290&count=250",
        "https://www.dacia.rs/wired/commerce/v1/dealers/locator?lat=44.91631454215744&lon=20.3272146911047&country=rs&language=sr&filters=dacia.blacklisted%3D%3Dfalse%3BbirId!%3D89150041%3Bbird!%3D89150176%3BbirId!%3D89150176&count=250",
    ]

    page_urls = {
        "de.dacia.ch": "https://de.dacia.ch/haendler-suchen.html",
        "fr.dacia.be": "https://fr.dacia.be/trouvez-votre-concessionnaire.html",
        "www.dacia.com.tr": "https://www.dacia.com.tr/yetkili-satici-bul.html",
        "www.dacia.cz": "https://www.dacia.cz/najit-dealera.html",
        "www.dacia.de": "https://www.dacia.de/haendlersuche.html",
        "www.dacia.dz": "https://www.dacia.dz/trouver-un-distributeur.html",
        "www.dacia.es": "https://www.dacia.es/concesionario.html",
        "www.dacia.fr": "https://www.dacia.fr/trouvez-votre-etablissement-dacia.html",
        "www.dacia.hr": "https://www.dacia.hr/pronadite-koncesionara.html",
        "www.dacia.hu": "https://www.dacia.hu/kereskedes-keresese.html",
        "www.dacia.it": "https://www.dacia.it/concessionario.html",
        "www.dacia.lu": "https://www.dacia.lu/trouvez-votre-concessionnaire.html",
        "www.dacia.ma": "https://www.dacia.ma/trouvez-un-concessionnaire.html",
        "www.dacia.nl": "https://www.dacia.nl/dealer-vinden.html",
        "www.dacia.pl": "https://www.dacia.pl/znajdz-dealera.html",
        "www.dacia.pt": "https://www.dacia.pt/concessionarios.html",
        "www.dacia.ro": "https://www.dacia.ro/reteaua-dacia.html",
        "www.dacia.rs": "https://www.dacia.rs/pronadji-distributera.html",
        "www.dacia.si": "https://www.dacia.si/poiscite-pooblascenega-prodajalca.html",
    }
    domain = "dacia.be"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        all_locations = session.get(start_url, headers=hdr).json()
        for poi in all_locations:
            item = SgRecord(
                locator_domain=domain,
                page_url=page_urls[start_url.split("/")[2]],
                location_name=poi["name"],
                street_address=poi["streetAddress"],
                city=poi["locality"],
                state="",
                zip_postal=poi.get("postalCode"),
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
