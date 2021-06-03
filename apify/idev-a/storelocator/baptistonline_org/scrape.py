from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("baptistonline")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://www.baptistonline.org"
base_url = "https://www.baptistonline.org/locations"

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=500,
    max_search_results=500,
)

urls = [
    "https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearchByType?query={}&dsiID={}&locationType=Clinic&uniqueID={}&radius=5000&bmgonly=true&contextid={}&_=1595841861300",
    "https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query={}&dsiID={}&locationType=Minor%20Medical&uniqueID={}&radius=%203000&contextid={}&_=1595842100608",
    "https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query={}&locationType=Specialty&dsiID={}&uniqueID={}&radius=%203000&contextid={}&_=1595842100610",
    "https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query={}&locationType=Hospital&dsiID={}&uniqueID={}&radius=%203000&contextid={}&_=1595842100607",
]

l_type = {
    "0": "Clinic",
    "1": "Minor Medical Centers",
    "2": "Speciality Facilities",
    "3": "Hospital",
}


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    sp1 = bs(session.get(base_url, headers=headers).text, "lxml")
    context_id = sp1.select_one("#hospitals div.location-list")["data-context-id"]
    dsiID = sp1.select_one('input[name="dsiID"]')["value"]
    unqID = sp1.select_one('input[name="unqID"]')["value"]
    maxZ = search.items_remaining()
    total = 0
    for zip in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        for index, _url in enumerate(urls):
            url = _url.format(zip, dsiID, unqID, context_id)
            logger.info(url)
            locations = bs(
                session.get(url, headers=headers, timeout=15).text, "lxml"
            ).select("ul li")
            total += len(locations)
            for loc_list in locations:
                store = {}
                try:
                    store["location_name"] = loc_list.select_one(
                        "p.location-name"
                    ).text.strip()
                except:
                    continue
                store["latitude"] = loc_list.find(
                    "input", {"name": "location-lat"}
                ).get("value", "<MISSING>")
                store["longitude"] = loc_list.find(
                    "input", {"name": "location-lng"}
                ).get("value", "<MISSING>")
                try:
                    page_url = loc_list.select_one("p.location-name a")["href"]
                    if "www.google.com/maps" not in page_url:
                        if "http" in page_url:
                            store["page_url"] = page_url
                        elif "/locations" in page_url:
                            store["page_url"] = (
                                "https://www.baptistonline.org" + page_url
                            )
                        else:
                            store["page_url"] = (
                                "https://www.baptistonline.org" + page_url
                            )

                    else:
                        store["page_url"] = "<MISSING>"
                except:
                    store["page_url"] = "<MISSING>"
                address = list(
                    loc_list.find("p", class_="location-address").stripped_strings
                )
                store["street_address"] = " ".join(address[:-1])
                store["city"] = address[-1].split(",")[0].strip()
                store["state"] = address[-1].split(",")[-1].split()[0].strip()
                store["zip_postal"] = address[-1].split(",")[-1].split()[-1].strip()
                store["phone"] = loc_list.find(
                    "a", class_="location-phone"
                ).text.strip()
                store["location_type"] = l_type[str(index)]
                yield store
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"[{zip}] found: {len(locations)} | total: {total} | progress: {progress}"
            )


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["page_url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["zip_postal"],
        ),
        country_code=sp.ConstantField("US"),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        location_type=sp.MappingField(
            mapping=["location_type"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        store_number=sp.MissingField(),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
