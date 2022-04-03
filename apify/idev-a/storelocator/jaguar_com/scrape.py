from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("jaguar")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.jaguar.com"
base_url = "https://www.jaguar.com/retailer-locator/index.html"
cn_url = "https://dealer.jaguar.com.cn/index.php?s=/JDealer/api/getDealerList&is_extend=11&is_lack=1"
us_url = "https://www.jaguarusa.com/retailer-locator/index.html?filter=All"


def parse_cn():
    with SgRequests(verify_ssl=False) as http:
        logger.info(cn_url)
        for _ in http.get(cn_url, headers=_headers).json()["data"]:
            street_address = _["addr"].split("市")[-1].replace(_["city_name"], "")
            hours = []
            if _["biz_hour_workday"]:
                hours.append(f"Monday to Friday: {_['biz_hour_workday']}")
            if _["biz_hour_weekend"]:
                hours.append(f"Monday to Friday: {_['biz_hour_weekend']}")

            yield SgRecord(
                page_url=_["url_jaguar"],
                store_number=_["dms_code"],
                location_name=_["dealer_name"],
                street_address=street_address,
                city=_["city_name"],
                state=_["province_name"],
                country_code="China",
                latitude=_["latitude"],
                longitude=_["longitude"],
                location_type="sales",
                phone=_["service_phone_jaguar"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["addr"],
            )


def _d(country, c_code, session, url, zip=None):
    logger.info(url)
    locations = bs(session.get(url, headers=_headers).text, "lxml").select(
        "div.listContainer ol > li > div.infoCardDealer"
    )
    if zip:
        logger.info(f"[uk] [{zip}] {len(locations)}")
    for _ in locations:
        phone = ""
        if _.select_one("span.phoneNumber"):
            phone = _.select_one("span.phoneNumber").text.strip()
        raw_address = _.select_one("span.addressText").text
        if country.lower() not in raw_address.lower():
            raw_address += ", " + country

        street_address = city = state = zip_postal = ""
        c_addr = [
            aa.strip()
            for aa in _.select_one("span.addressText")
            .text.replace("CP,", "")
            .strip()
            .split(",")
            if aa.strip()
        ]
        if c_code == "KR":
            zip_postal = c_addr[-1].strip()
            c_idx = -3
            if c_addr[-2].endswith("do") or c_addr[-2] == "Seoul":
                state = c_addr[-2].strip()
            else:
                c_idx += 1
            city = c_addr[c_idx].strip()
            street_address = ", ".join(c_addr[:c_idx])
        elif c_code in [
            "IL",
            "SA",
            "RS",
            "SK",
            "SE",
            "MA",
            "OM",
            "TN",
            "BG",
            "GR",
            "HU",
        ]:
            zip_postal = c_addr[-1].strip()
            s_idx = -2
            city = c_addr[-2].strip()
            if "P.O." in city:
                city = c_addr[-3].strip()
                s_idx -= 1
            street_address = ", ".join(c_addr[:s_idx])
        elif c_code == "MX":
            if not city and not state:
                city = c_addr[-2].strip()
                street_address = (
                    ", ".join(c_addr[:-2])
                    .replace(city, "")
                    .replace("Mexico", "")
                    .strip()
                )
        elif c_code in ["PA", "CL", "US"]:
            zip_postal = c_addr[-1]
            state = c_addr[-2]
            city = c_addr[-3]
            street_address = ", ".join(c_addr[:-3])
        else:
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            zip_postal = addr.postcode

        if c_code == "UK":
            zip_postal = c_addr[-1]
            if city.lower() in zip_postal.lower():
                city = c_addr[-2]

        if c_code == "TR":
            if (
                not city
                and not state
                and not zip_postal == ""
                or (city and city.isdigit())
            ):
                zip_postal = c_addr[-1].strip()
                state = c_addr[-2].strip()
                city = c_addr[-3].strip()
                street_address = ", ".join(c_addr[:-3])

        if c_code == "TH":
            if not city and "Bangkok" in raw_address:
                city = "Bangkok"

        if c_code == "PH":
            if "Metro Manila" in raw_address:
                state = "Metro Manila"

        if not street_address or street_address and street_address.isdigit():
            street_address = raw_address.split(",")[0]
        if city and city.isdigit():
            city = ""

        while True:
            if street_address and street_address.endswith(","):
                street_address = street_address[:-1]
            else:
                break

        yield SgRecord(
            page_url=url,
            store_number=_["data-ci-code"],
            location_name=_.select_one("h3 span.dealerNameText").text.strip(),
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country,
            phone=phone,
            latitude=_["data-lat"],
            longitude=_["data-lng"],
            location_type=", ".join(_.select_one("ul.services").stripped_strings),
            locator_domain=locator_domain,
            raw_address=raw_address,
        )


def parse_us():
    with SgRequests() as session:
        sp0 = bs(session.get(us_url, headers=_headers).text, "lxml")
        regions = sp0.select("select.regionSelect option")
        for region in regions:
            s_code = region["value"]
            if s_code == "0":
                continue
            state_url = f"https://www.jaguarusa.com/retailer-locator/index.html?region={s_code}&filter=All"
            for rec_intl in _d("United States", "US", session, state_url):
                yield rec_intl


def fetch_uk():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=100
    )
    for zip in search:
        url = f"https://www.jaguar.co.uk/national-dealer-locator.html?postCode={zip.replace(' ', '')}&filter=All"
        with SgRequests() as session:
            for rec_intl in _d("United Kingdom", "UK", session, url, search):
                yield rec_intl


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        countries = soup.select("select.DropdownSelectA11y")[0].select("option")
        for country in countries:
            c_code = country["value"]
            if c_code == "0":
                continue

            if c_code == "CN":
                for rec_cn in parse_cn():
                    yield rec_cn
                continue

            if c_code == "GB":
                continue

            if c_code == "US":
                for rec_us in parse_us():
                    yield rec_us
                continue

            url = f"https://www.jaguar.com/retailer-locator/index.html?country={c_code}&filter=All"
            for rec_intl in _d(country.text.strip(), c_code, session, url):
                yield rec_intl


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        for rec in fetch_uk():
            writer.write_row(rec)

        for rec in fetch_data():
            writer.write_row(rec)
