from lxml import html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    max_distance = 50

    coords = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.BRITAIN,
            SearchableCountries.FRANCE,
            SearchableCountries.ITALY,
            SearchableCountries.IRELAND,
        ],
        max_radius_miles=max_distance,
    )

    for lat, lon in coords:

        data = {
            "dwfrm_storelocator_countryCode": "",
            "dwfrm_storelocator_latitude": lat,
            "dwfrm_storelocator_longitude": lon,
            "dwfrm_storelocator_departments": "",
            "wideSearch": "false",
            "dwfrm_storelocator_findbylocation": "",
        }

        r = session.post(
            "https://www.gap.eu/on/demandware.store/Sites-ShopEU-Site/en_EE/Stores-Find",
            data=data,
        )
        tree = html.fromstring(r.text)
        ids = tree.xpath(
            "//div[@class='js-store-result js-store-result-box store-search-page__result']/@data-id"
        )

        for _id in ids:
            locator_domain = "https://www.gap.eu/"

            page_url = f"https://www.gap.eu/storesinformation?StoreID={_id}"

            r = session.get(page_url)
            tree = html.fromstring(r.text)

            street_address = (
                "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).strip()
                or "<MISSING>"
            )
            city = (
                "".join(
                    tree.xpath("//span[@itemprop='addressLocality']/text()")
                ).strip()
                or "<MISSING>"
            )
            state = "<MISSING>"
            postal = (
                "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
                or "<MISSING>"
            )
            country_code = (
                "".join(tree.xpath("//span[@itemprop='addressCountry']/text()")).strip()
                or "<MISSING>"
            )
            store_number = _id
            phone = (
                "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
                or "<MISSING>"
            )
            latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or ""
            longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng")) or ""

            if latitude:
                coords.found_location_at(float(latitude), float(longitude))

            location_type = (
                "".join(
                    tree.xpath("//div[@class='store-locator-details__details']/text()")
                )
                .strip()[:-1]
                .strip()
                or "<MISSING>"
            )
            if location_type.startswith(","):
                location_type = location_type.replace(",", "").strip()

            if "," in location_type:
                location_name = "Gap"
            else:
                location_name = location_type

            hours = tree.xpath("//span[@class='store-hours']//text()")
            hours = list(filter(None, [h.strip() for h in hours]))
            hours_of_operation = (
                ";".join(hours)
                .replace(
                    "due to covid restrictions this store is temporarily closed, please visit www.gap.co.uk;",
                    "",
                )
                .replace("p>;", "")
                .replace(";>", "")
                or "<MISSING>"
            )
            if "opening times.;" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("opening times.;")[
                    1
                ].strip()

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
