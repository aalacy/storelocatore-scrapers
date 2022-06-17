# -*- coding: utf-8 -*-
from w3lib.url import url_query_parameter
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch


def fetch_data():
    session = SgRequests()
    start_urls = [
        "https://www.dacia.si/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=si&language=sl&count=500",
        "https://de.dacia.ch/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=ch&language=de&count=500",
        "https://fr.dacia.be/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=be&language=fr&count=500",
        "https://www.dacia.com.tr/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=tr&language=tr&count=500",
        "https://www.dacia.cz/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=cz&language=cs&count=500",
        "https://www.dacia.de/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=de&language=de&count=500",
        "https://www.dacia.dz/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=dz&language=fr&count=500",
        "https://www.dacia.es/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=es&language=es&count=500",
        "https://www.dacia.fr/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=fr&language=fr&count=500",
        "https://www.dacia.hr/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=hr&language=hr&count=500",
        "https://www.dacia.hu/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=hu&language=hu&count=500",
        "https://www.dacia.it/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=it&language=it&count=500",
        "https://www.dacia.lu/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=lu&language=fr&count=500",
        "https://www.dacia.ma/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=ma&language=fr&count=500",
        "https://www.dacia.nl/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=nl&language=nl&count=500",
        "https://www.dacia.pl/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=pl&language=pl&count=500",
        "https://www.dacia.ro/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=ro&language=ro&count=500",
        "https://www.dacia.rs/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=rs&language=sr&count=500",
        "https://www.dacia.pt/wired/commerce/v1/dealers/locator?lat={}&lon={}&country=pt&language=pt&count=500",
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
        "www.dacia.pt": "https://www.dacia.pt/concessionarios.html",
    }
    domain = "dacia.be"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        country_code = url_query_parameter(start_url, "country")
        all_coords = DynamicGeoSearch(
            country_codes=[country_code], expected_search_radius_miles=50
        )
        for lat, lng in all_coords:
            all_locations = session.get(start_url.format(lat, lng), headers=hdr).json()
            if not all_locations:
                all_coords.found_nothing()
            for poi in all_locations:
                latitude = poi.get("geolocalization", {}).get("lat")
                longitude = poi.get("geolocalization", {}).get("lon")
                all_coords.found_location_at(lat, lng)
                if not poi["name"]:
                    continue

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_urls[start_url.split("/")[2]],
                    location_name=poi["name"],
                    street_address=poi["streetAddress"],
                    city=poi["locality"].split(",")[0],
                    state="",
                    zip_postal=poi.get("postalCode"),
                    country_code=poi["country"],
                    store_number=poi["dealerId"],
                    phone=poi["telephone"].get("value"),
                    location_type=poi["type"],
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation="",
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
