from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_additional(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    try:
        phones = tree.xpath(
            "//a[contains(@href, 'tel:')]/text()|//div[@class='b-map-detail__phone']/span/text()"
        )
        phones = list(filter(None, [p.strip() for p in phones]))
        phone = phones[0]
    except:
        phone = SgRecord.MISSING

    hours = tree.xpath(
        "//h4[contains(text(), 'Horarios')]/following-sibling::p//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    return phone, hours_of_operation


def fetch_data(sgw: SgWriter):
    apis = [
        "https://www.cemexmexico.com/donde-estamos-ubicados?p_p_id=CEMEX_MAP_SEARCH&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=findTheNearestLocations&p_p_cacheability=cacheLevelPage&_CEMEX_MAP_SEARCH_locationName=M%C3%A9xico",
        "https://www.cemex.pl/znajdz-swoja-lokalizacje?p_p_id=CEMEX_MAP_SEARCH&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=findTheNearestLocations&p_p_cacheability=cacheLevelPage&_CEMEX_MAP_SEARCH_locationName=Polska",
        "https://www.cemex.hr/lokacije?p_p_id=CEMEX_MAP_SEARCH&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=findTheNearestLocations&p_p_cacheability=cacheLevelPage&_CEMEX_MAP_SEARCH_locationName=Hrvatska",
        "https://www.cemex.fr/implantations?p_p_id=CEMEX_MAP_SEARCH&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=findTheNearestLocations&p_p_cacheability=cacheLevelPage&_CEMEX_MAP_SEARCH_locationName=R%C3%A9publique%20fran%C3%A7aise",
        "https://www.cemex.es/acerca-de-cemex/donde-estamos-ubicados?p_p_id=CEMEX_MAP_SEARCH&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=findTheNearestLocations&p_p_cacheability=cacheLevelPage&_CEMEX_MAP_SEARCH_locationName=Espa%C3%B1a",
        "https://www.cemex.de/standorte?p_p_id=CEMEX_MAP_SEARCH&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=findTheNearestLocations&p_p_cacheability=cacheLevelPage&_CEMEX_MAP_SEARCH_locationName=Deutschland",
        "https://www.cemex.cz/betonarny-cementarny-kamenolomy-piskovny?p_p_id=CEMEX_MAP_SEARCH&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=findTheNearestLocations&p_p_cacheability=cacheLevelPage&_CEMEX_MAP_SEARCH_locationName=%C4%8Cesk%C3%A1%20republika",
    ]
    for api in apis:
        locator_domain = "/".join(api.split("/")[:3])
        country = locator_domain.split(".")[-1].upper()
        if country == "COM":
            country = "MX"

        r = session.get(api, headers=headers)
        for j in r.json()["theNearestLocations"]:
            slug = j.get("url")
            page_url = f"{locator_domain}/-/{slug}"
            location_name = j.get("locationName")

            a = j.get("locationAddress") or {}
            street_address = a.get("locationStreet")
            city = a.get("locationCity")
            state = a.get("locationRegion")
            postal = a.get("locationPostcode")

            g = a.get("locationCoordinates") or {}
            latitude = g.get("latitude")
            longitude = g.get("longitude")

            l = j.get("locationContact") or {}
            phone = l.get("locationOrdersPhone") or ""
            if "," in phone:
                phone = phone.split(",")[0].strip()
            if "@" in phone:
                phone = SgRecord.MISSING
            if "T:" in phone:
                phone = phone.replace("T:", "").strip()

            hours_of_operation = j.get("openingHours") or ""
            if "<br>" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("<br>")[0].strip()
            if "<" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("<")[0].strip()

            if not phone and not hours_of_operation:
                try:
                    phone, hours_of_operation = get_additional(page_url)
                except:
                    pass
            if ":" in phone:
                phone = phone.split(":")[-1].strip()

            row = SgRecord(
                location_name=location_name,
                page_url=page_url,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
