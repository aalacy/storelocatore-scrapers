from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://esso.co.uk/"
urls = [
    "https://www.esso.co.uk/en-GB/api/locator/Locations?Latitude1=48.356492210436045&Latitude2=60.94128404594158&Longitude1=-22.645048209150662&Longitude2=16.246553353349338&DataSource=RetailGasStations&Country=GB&Customsort=False",
    "https://www.esso.co.uk/en-GB/api/locator/Locations?Latitude1=50.74676814707322&Latitude2=52.45255064522355&Longitude1=-3.666406883682063&Longitude2=1.195043311630437&DataSource=RetailGasStations&Country=GB&Customsort=False",
    "https://www.esso.be/nl-BE/api/locator/Locations?Latitude1=50.624922158805276&Latitude2=51.058510546220255&Longitude1=3.7564227097168157&Longitude2=4.970755290283222&DataSource=RetailGasStations&Country=BE&Customsort=False",
    "https://www.esso.com.cy/en-CY/api/locator/Locations?Latitude1=34.85303102955643&Latitude2=35.41457235947357&Longitude1=32.703455109716806&Longitude2=33.91778769028321&DataSource=RetailGasStations&Country=CY&Customsort=False",
    "https://carburant.esso.fr/fr-FR/api/locator/Locations?Latitude1=48.632563594978365&Latitude2=49.084318313537196&Longitude1=1.6701793097167839&Longitude2=2.88451189028319&DataSource=RetailGasStations&Country=FR&Customsort=False",
    "https://www.esso.de/de-DE/api/locator/Locations?Latitude1=53.354268442922766&Latitude2=53.76213590985459&Longitude1=9.180229609716788&Longitude2=10.394562190283194&DataSource=RetailGasStations&Country=DE&Customsort=False",
    "https://carburanti.esso.it/it-IT/api/locator/Locations?Latitude1=41.65423184574465&Latitude2=42.16522772384339&Longitude1=11.788404509716809&Longitude2=13.002737090283215&DataSource=RetailGasStations&Country=IT&Customsort=False",
    "https://www.esso.lu/fr-LU/api/locator/Locations?Latitude1=49.38470792669541&Latitude2=49.82966673967849&Longitude1=5.458492409716786&Longitude2=6.672824990283193&DataSource=RetailGasStations&Country=LU&Customsort=False",
    "https://www.esso.nl/nl-NL/api/locator/Locations?Latitude1=51.71584742810264&Latitude2=52.13926829392299&Longitude1=3.8130205097168046&Longitude2=5.027353090283211&DataSource=RetailGasStations&Country=NL&Customsort=False",
    "https://www.esso.no/nb-NO/api/locator/Locations?Latitude1=59.72129423961607&Latitude2=60.06571805792095&Longitude1=10.037525509716788&Longitude2=11.251858090283195&DataSource=RetailGasStations&Country=NO&Customsort=False",
    "https://www.esso.com.hk/en-HK/api/locator/Locations?Latitude1=21.989977698337693&Latitude2=22.625229862346522&Longitude1=113.56872370971679&Longitude2=114.7830562902832&DataSource=RetailGasStations&Country=HK&Customsort=True",
    "https://www.esso.com.sg/en-SG/api/locator/Locations?Latitude1=1.0576334463431816&Latitude2=1.744069623810626&Longitude1=102.94707403767096&Longitude2=104.16140661823736&DataSource=RetailGasStations&Country=SG&Customsort=False",
    "https://www.fuels.esso.co.th/en-TH/api/locator/Locations?Latitude1=13.665169713849096&Latitude2=13.831912603975242&Longitude1=100.38607142742919&Longitude2=100.68965457257079&DataSource=RetailGasStations&Country=TH&Customsort=True",
]

locators = [
    "https://www.esso.co.uk/en-gb/find-station/",
    "https://www.esso.co.uk/en-gb/find-station/",
    "https://www.esso.be/nl-be/find-station/",
    "https://www.esso.com.cy/en-cy/find-station/",
    "https://carburant.esso.fr/fr-fr/find-station/",
    "https://www.esso.de/de-de/find-station/",
    "https://carburanti.esso.it/it-it/find-station/",
    "https://www.esso.lu/fr-lu/find-station/",
    "https://www.esso.nl/nl-nl/find-station/",
    "https://www.esso.no/nb-no/find-station/",
    "https://www.esso.com.hk/en-hk/find-station/",
    "https://www.esso.com.sg/en-sg/find-station/",
    "https://www.fuels.esso.co.th/en-th/find-station/",
]


def fetch_data():
    with SgRequests() as session:
        for x, base_url in enumerate(urls):
            country = base_url.split("Country=")[1].split("&")[0]
            locations = session.get(base_url, headers=_headers).json()
            for _ in locations:
                street_address = _["AddressLine1"]
                if _["AddressLine2"]:
                    street_address += " " + _["AddressLine2"]

                hours = []
                if _["WeeklyOperatingHours"]:
                    hours = bs(_["WeeklyOperatingHours"], "lxml").stripped_strings
                city = _["City"]
                state = _["StateProvince"]
                if city:
                    cc = city.split(",")
                    if not state and len(cc) > 1:
                        city = cc[0]
                        state = cc[1]

                page_url = f"{locators[x]}esso-{city.lower()}-{re.sub(r'[^a-zA-Z]', '', _['DisplayName'].lower())}-{_['LocationID']}"
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["LocationID"],
                    location_name=_["LocationName"],
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=_["PostalCode"],
                    latitude=_["Latitude"],
                    longitude=_["Longitude"],
                    country_code=country,
                    phone=_["Telephone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
