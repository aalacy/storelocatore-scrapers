from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, Grain_8
from sgzip.utils import country_names_by_code
from fuzzywuzzy import process
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json


logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
known_empties = set()
known_empties.add("xxxxxxx")

errorz = []


def get_Start(session, headers):
    page = session.get("https://locate.apple.com/findlocations", headers=headers)
    soup = b4(page.text, "lxml")
    data = []
    soup = soup.find("div", {"class": "content selfclear", "id": "content"}).find_all(
        "li"
    )
    for i in soup:
        name = i.find("span").text
        link = i.find("a")["href"]
        found = False
        for index, country in enumerate(data):
            if link.split("/")[1] == country["link"].split("/")[1]:
                if "/en/" in link:
                    data[index]["link"] = link
                    data[index]["name"] = name
                found = True
        if not found:
            if len(link) > 7:
                data.append({"name": name, "link": link, "special": True})
            else:
                data.append({"name": name, "link": link, "special": False})
    return data


def determine_country(country):
    Searchable = country_names_by_code()
    resultName = process.extract(country["name"], list(Searchable.values()), limit=1)
    resultCode = process.extract(
        country["link"].split("/")[1], list(Searchable.keys()), limit=1
    )
    logzilla.info(
        f"Matched {country['name']}{country['link']} to {resultName[0]} or {resultCode[0]}"
    )
    if resultName[-1][-1] > resultCode[-1][-1]:
        for i in Searchable.items():
            if i[1] == resultName[-1][0]:
                return i[0]
    else:
        return resultCode[-1][0]


def get_country(search, country, session, headers, SearchableCountry):
    def getPoint(point, session, locale, headers):
        if locale[-1] != "/":
            locale = locale + "/"
        url = "https://locate.apple.com{locale}sales/?pt=all&lat={lat}&lon={lon}&address=".format(
            locale=locale, lat=point[0], lon=point[1]
        )
        result = session.get(url, headers=headers)
        soup = b4(result.text, "lxml")
        allscripts = soup.find_all("script")
        thescript = None
        for i in allscripts:
            if "window.resourceLocator.storeSetup" in i.text:
                thescript = i
        if thescript:
            thescript = thescript.text
            thescript = (
                thescript.split("window.resourceLocator.storeSetup = ", 1)[1]
                .rsplit("if(", 1)[0]
                .rsplit(";", 1)[0]
            )
        try:
            locs = json.loads(thescript)
            return locs["results"]
        except Exception as e:
            errorz.append(
                str(
                    f"had some issues with this country and point  {country}\n{point}{url} \n Matched to: {SearchableCountry}\nIssue was\n{str(e)}"
                )
            )

    maxZ = None
    maxZ = search.items_remaining()
    total = 0
    for Point in search:
        found = 0
        for record in getPoint(Point, session, country["link"], headers):
            search.found_location_at(
                record["locationData"]["geo"][0], record["locationData"]["geo"][1]
            )
            record["COUNTRY"] = country
            found += 1
            yield record
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logzilla.info(
            f"{str(Point).replace('(','').replace(')','')}|found: {found}|total: {total}|prog: {progress}|\nRemaining: {search.items_remaining()} Searchable: {SearchableCountry}"
        )
    if total == 0:
        logzilla.error(
            f"Found a total of 0 results for country {country}\n this is unacceptable and possibly a country/search space mismatch\n Matched to: {SearchableCountry}"
        )
        if SearchableCountry not in known_empties:
            errorz.append(
                str(
                    f"Found a total of 0 results for country {country}\n this is unacceptable and possibly a country/search space mismatch\n Matched to: {SearchableCountry}"
                )
            )


def fetch_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    with SgRequests() as session:
        countries = get_Start(session, headers)
        for country in countries:
            if country["special"]:
                pass
            else:
                SearchableCountry = determine_country(country)
                search = False
                try:
                    search = DynamicGeoSearch(
                        country_codes=[SearchableCountry],
                        max_radius_miles=50,
                        max_search_results=None,
                        granularity=Grain_8(),
                    )
                except Exception as e:
                    logzilla.info(
                        f"Issue with sgzip and country code: {SearchableCountry}\n{e}"
                    )
                if search:
                    for record in get_country(
                        search, country, session, headers, SearchableCountry
                    ):
                        yield record
    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def scrape():
    url = "locate.apple.com"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["storeURL"],
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["storeName"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["locationData", "geo", 0],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["locationData", "geo", 1],
            is_required=False,
        ),
        street_address=sp.MultiMappingField(
            mapping=[
                ["locationData", "streetAddress1"],
                ["locationData", "streetAddress2"],
            ],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["locationData", "city"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["locationData", "state"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["locationData", "postalCode"],
            is_required=False,
        ),
        country_code=sp.MappingField(
            mapping=["locationData", "country"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["phoneNumber"],
            part_of_record_identity=True,
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["storeID"],
            part_of_record_identity=True,
            is_required=False,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MissingField(),
        raw_address=sp.MultiMappingField(
            mapping=[["locationData", "district"], ["locationData", "regionName"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
            is_required=False,
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=25,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
    for i in errorz:
        logzilla.info(i)
    raise
