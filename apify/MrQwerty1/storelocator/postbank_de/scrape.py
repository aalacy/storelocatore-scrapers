import math
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import sglog
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def get_bounds(latitude, longitude, distance):
    radius = 6371

    lat = math.radians(latitude)
    lng = math.radians(longitude)
    parallel_radius = radius * math.cos(lat)

    lat_min = lat - distance / radius
    lat_max = lat + distance / radius
    lon_min = lng - distance / parallel_radius
    lon_max = lng + distance / parallel_radius
    rad2deg = math.degrees

    lat_min = rad2deg(lat_min)
    lng_min = rad2deg(lon_min)
    lat_max = rad2deg(lat_max)
    lng_max = rad2deg(lon_max)

    bounds = f"{lng_min}%2C{lng_max}%2C{lat_min}%2C{lat_max}"
    return bounds


def get_hoo(url):
    _tmp = []
    r = session.get(url, headers=headers)
    logger.info(f"{url}: {r}")
    tree = html.fromstring(r.text)

    hours = tree.xpath(
        "//h3[contains(text(), 'Filiale')]/following-sibling::div//div[contains(@class, 'dayOfTheWeek')]"
    )
    for h in hours:
        day = "".join(h.xpath(".//text()")).strip()
        inter = "|".join(h.xpath("./following-sibling::div[1]/p/text()"))
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    ids = set()
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.GERMANY], expected_search_radius_miles=10
    )

    for lat, lng in search:
        bounds = get_bounds(lat, lng, 15)
        api = f"https://www.postbank.de/cip/rest/api/url/dienste/gdata/Presentation/PostbankFinder/Home/IndexJson?open=0&alwaysOpen=0&test=false&label=BRANCH&locale=&bounds={bounds}"
        r = session.get(api, headers=headers)
        logger.info(f"{api}: {r}")
        source = r.json().get("html") or "<html>"
        tree = html.fromstring(source)
        divs = tree.xpath("//div[@class='result-item']")

        for d in divs:
            line = d.xpath(".//address/p/text()")
            street_address = line.pop(0)
            zc = line.pop(0)
            postal = zc.split()[0]
            city = zc.replace(postal, "")
            if "(" in city:
                city = city.split("(")[0].strip()
            if "/" in city:
                city = city.split("/")[0].strip()

            country_code = "DE"
            store_number = "".join(d.xpath("./@data-id"))
            location_name = "".join(d.xpath(".//address/span/text()")).strip()
            page_url = f"https://www.postbank.de/cip/rest/api/url/dienste/gdata/Presentation/PostbankFinder/Home/Details/{store_number}"

            if store_number in ids:
                continue
            ids.add(store_number)

            try:
                text = d.xpath(".//a/@data-coords")[0]
                latitude, longitude = text.split(",")
            except:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            hours_of_operation = get_hoo(page_url)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                store_number=store_number,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.postbank.de/"
    logger = sglog.SgLogSetup().get_logger("postbank.de")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
