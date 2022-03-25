from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://tiendeo.com/shopping-centers"
urls = {
    "US": "https://www.tiendeo.us/malls",
    "Canada": "https://tiendeo.ca/shopping-centres",
    "UK": "https://www.tiendeo.co.uk/shopping-centres",
    "Australia": "https://www.tiendeo.com.au/shopping-centres",
    "Spain": "https://www.tiendeo.com/centros-comerciales",
    "Italy": "https://www.tiendeo.it/centri-commerciali",
    "Brazil": "https://www.tiendeo.com.br/shoppings",
    "Colombia": "https://www.tiendeo.com.co/centros-comerciales",
    "Argentina": "https://www.tiendeo.com.ar/shoppings",
    "India": "https://www.tiendeo.in/malls",
    "France": "https://www.tiendeo.fr/centres-commerciaux",
    "The Netherlands": "https://www.tiendeo.nl/winkelcentra",
    "Germany": "https://www.tiendeo.de/Einkaufszentren",
    "Peru": "https://www.tiendeo.pe/centros-comerciales",
    "Chile": "https://www.tiendeo.cl/malls",
    "Portugal": "https://www.tiendeo.pt/shoppings",
    "Russia": "https://www.tiendeo.ru/torgovye-centry",
    "Turkey": "https://www.tiendeo.com.tr/alisveris-merkezleri",
    "Polish": "https://www.tiendeo.pl/centra-handlowe",
    "Norway": "https://www.tiendeo.no/kj%C3%B8pesentre",
    "Austria": "https://www.tiendeo.at/Einkaufszentren",
    "Sweden": "https://www.tiendeo.se/koepcentrum",
    "Ecuador": "https://www.tiendeo.com.ec/centros-comerciales",
    "Singapore": "https://www.tiendeo.sg/Malls",
    "Indonesia": "https://www.tiendeo.co.id/malls",
    "Malaysia": "https://www.tiendeo.my/shopping-centres",
    "South Africa": "https://www.tiendeo.co.za/malls",
    "Denmark": "https://www.tiendeo.dk/indk%C3%B8bscentre",
    "Finland": "https://www.tiendeo.fi/indeksi-ostoskeskuksia",
    "New Zealand": "https://www.tiendeo.co.nz/malls",
    "Japan": "https://www.tiendeo.jp/%E3%82%B7%E3%83%A7%E3%83%83%E3%83%94%E3%83%B3%E3%82%B0%E3%83%A2%E3%83%BC%E3%83%AB",
    "Greek": "https://www.tiendeo.gr/%CE%B5%CE%BC%CF%80%CE%BF%CF%81%CE%B9%CE%BA%CE%AC-%CE%BA%CE%AD%CE%BD%CF%84%CF%81%CE%B1",
    "South Korea": "https://www.tiendeo.co.kr/%EC%87%BC%ED%95%91%EB%AA%B0",
    "Belgium": "https://www.tiendeo.be/fr/centres-commerciaux",
    "Switzerland": "https://www.tiendeo.ch/einkaufszentren",
    "UAE": "https://www.tiendeo.ae/malls",
    "Ukraine": "https://www.tiendeo.com.ua/torhovi-tsentry",
    "Romania": "https://www.tiendeo.ro/mall",
    "Maroku": "https://www.tiendeo.ma/centres-commerciaux",
    "Czech Republic": "https://www.tiendeo.cz/nakupni-strediska",
    "Slovakia": "https://www.tiendeo.sk/nakupnych-centier",
    "Hungary": "https://www.tiendeo.hu/bevasarlokozpontok",
    "Bulgaria": "https://www.tiendeo.bg/molove",
}

hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def _d(loc, domain, country):
    with SgRequests() as session:
        try:
            page_url = domain + loc["url"]["url"]
            logger.info(page_url)
            info = json.loads(
                bs(session.get(page_url, headers=_headers).text, "lxml")
                .select_one("script#__NEXT_DATA__")
                .text
            )["props"]["pageProps"]["queryResult"]
            if not info.get("MallInfo"):
                return None
            _ = info["MallInfo"]
            raw_address = f"{_['address']}, {_['city']}"
            if _["zipCode"]:
                raw_address += f", {_['zipCode']}"
            raw_address += f", {country}"
            addr = parse_address_intl(raw_address)
            city = addr.city
            if city and city.lower() == "city":
                city = ""
            state = addr.state
            hours = []
            phone = ""
            if _["time"]:
                hr = bs(_["time"], "lxml")
                if hr.table:
                    for hh in hr.table.select("tr"):
                        _pp = hh.text.strip()
                        if not _pp and hours:
                            break
                        if not _pp:
                            continue
                        if not hours and (
                            "Hours" in _pp or "Day" in _pp or "Woolworths" in _pp
                        ):
                            continue
                        if hours and "Hours" in _pp:
                            break
                        td = hh.select("td")
                        if len(td) < 2:
                            break
                        hours.append(f"{td[0].text.strip()} {td[1].text.strip()}")
                elif hr.select("OpeningDay"):
                    temp = [pp.text.strip() for pp in hr.select("p")]
                    for x in range(0, len(temp), 2):
                        hours.append(f"{temp[x]}: {temp[x+1]}")
                elif hr.select("dl.schedule"):
                    hours = [pp.text.strip() for pp in hr.select("dl.schedule")]
                elif hr.select("ul li"):
                    for hh in hr.select("ul li"):
                        hours.append(hh.text.strip())
                elif len(hr.select("p")) > 1:
                    for pp in hr.select("p"):
                        _pp = pp.text.strip()
                        if not _pp and hours:
                            break
                        if hours:
                            if (
                                "LOJAS:" in _pp
                                or "Orari" in _pp
                                or "Ipermercato" in _pp
                                or "Coop" in _pp
                                or "food" in _pp
                                or "horario" in _pp.lower()
                            ):
                                break
                        if (
                            "Merk" in _pp
                            or "Apotheke" in _pp
                            or "ATRIO" in _pp
                            or "Interspar" in _pp
                            or "Kino" in _pp
                            or "ストラン" in _pp
                            or "Restaurants" in _pp
                            or "飲食店" in _pp
                            or "Gastronomie" in _pp
                            or "maximarkt" in _pp.lower()
                            or "Café" in _pp
                            or "INTERSPAR" in _pp
                            or "Modeabteilung" in _pp
                            or "Lebensmittel" in _pp
                            or "INTERSPAR" in _pp
                            or "Fitness" in _pp
                            or "Individual" in _pp
                            or "Restaurant" in _pp
                            or "NICKELODEON" in _pp
                            or "Nordstrom" in _pp
                        ):
                            break
                        if not hours:
                            if "Opening" in _pp:
                                break
                            if _pp.lower().endswith("hours"):
                                continue
                        if not _pp:
                            continue
                        if "TRAISENPARK" in _pp or "Q19" in _pp:
                            continue
                        if _pp == "Lojas" or _pp == "Galleria" or _pp == "COOP":
                            continue

                        temp = []
                        for tt in list(pp.stripped_strings):
                            if hours:
                                if (
                                    "NEGOZI" in tt
                                    or "restauración" in tt.lower()
                                    or "cafeterías" in tt.lower()
                                    or "Hipermercado" in tt
                                    or "hours" in tt.lower()
                                    or "opening" in tt.lower()
                                    or tt.lower().endswith("hours")
                                    or "Monday" in tt.lower()
                                ):
                                    break
                                if _p(tt):
                                    phone = tt
                                    break
                            if (
                                "Öffnungszeiten" in tt
                                or "galerii" in tt
                                or "shop" in tt.lower()
                                or "Część" in tt
                                or "Galerii" in tt
                                or "handlowe" in tt
                                or "Godziny otwarcia" in tt
                                or "Galeria" in tt
                                or "Centre" in tt
                                or "centro" in tt.lower()
                                or "NEGOZI" in tt
                                or "please" in tt.lower()
                                or "Choc Deli" in tt
                            ):
                                continue
                            if (
                                "Auchan" in tt.lower()
                                or "rozrywkowa" in tt.lower()
                                or "Carrefour" in tt
                                or "Sklep" in tt
                                or "supermarketu" in tt.lower()
                                or "Apteki" in tt
                                or "hipermarketu" in tt.lower()
                                or "Showcase" in tt
                                or "store" in tt.lower()
                                or "Academia" in tt
                                or "Alimentação" in tt
                                or "LIVELLO" in tt
                                or "Supermercato" in tt
                                or "Ristoranti" in tt
                                or "Ristorazione" in tt
                            ):
                                break

                            temp.append(tt.split("soboty")[-1].split("*")[0].strip())
                        hours.append(" ".join(temp))
                elif hr.select("div.field__item"):
                    hours = [
                        " ".join(pp.stripped_strings)
                        for pp in hr.select("div.field__item")
                    ]
            hours_of_operation = (
                "; ".join(hours)
                .replace("ョップ：", "")
                .replace("ョップ：", "")
                .replace("Lojas", "")
                .replace(".", "")
                .replace("La galleria", "")
                .replace("Galleria Commerciale e Ristorazione:", "")
                .replace("GALLERIA COMMERCIALE", "")
                .replace("Shops / Food Gallery", "")
                .replace("Horario Simply Market", "")
                .strip()
            )
            if hours_of_operation.startswith(":"):
                hours_of_operation = hours_of_operation[1:]
            if hours_of_operation.startswith(","):
                hours_of_operation = hours_of_operation[1:]
            if hours_of_operation.endswith(";"):
                hours_of_operation = hours_of_operation[:-1]

            hours_of_operation = " ".join(
                [h_s.strip() for h_s in hours_of_operation.split(" ") if h_s.strip()]
            )
            return SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"],
                city=city,
                state=state,
                zip_postal=_.get("zipCode"),
                country_code=country,
                phone=_.get("phone") or phone,
                latitude=_.get("lat"),
                longitude=_.get("lon"),
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation.replace(";;", ";"),
                raw_address=raw_address,
            )
        except Exception as e:
            pass


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            domain = "/".join(base_url.split("/")[:3])
            malls = json.loads(
                bs(session.get(base_url, headers=_headers).text, "lxml")
                .select_one("script#__NEXT_DATA__")
                .text
            )["props"]["pageProps"]["queryResult"]["Malls"]["nodes"]
            for mall in malls:
                yield _d(mall, domain, country)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
