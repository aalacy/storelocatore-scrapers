import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import SearchableCountries

session = SgRequests()


def fetch_data(sgw: SgWriter):
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers1 = {"User-Agent": user_agent}

    countries = SearchableCountries.WITH_COORDS_ONLY
    countries.extend(SearchableCountries.WITH_ZIPCODE_AND_COORDS)
    countries.sort()

    us_url = "https://www.bmwusa.com/api/dealers/search?query=BMW"
    us_locs = session.get(us_url, headers=headers).json()

    for i in countries:
        country = i.upper()
        if country in addresses:
            continue
        addresses.append(country)

        r1 = session.get(
            "https://c2b-services.bmw.com/c2b-localsearch/services/api/v4/clients/BMWSTAGE2_DLO/%s/pois?brand=BMW_BMWM&cached=off&callback=angular.callbacks._0&category=BM&country=%s&language=en&lat=0&lng=0&maxResults=2000&showAll=true&unit=km"
            % (country, country),
            headers=headers,
        )
        soup1 = BeautifulSoup(r1.text, "lxml")
        jd = str(soup1).split("angular.callbacks._0(")[1].split(")</p>")[0]
        json_data = json.loads(jd)["data"]["pois"]
        for value in json_data:
            locator_domain = "https://www.bmw.com/"
            location_name = value["name"].replace("amp;", "")
            street_address = value["street"].replace("Jr.", "Jr").replace("amp;", "")
            if street_address[-1:] == ".":
                street_address = street_address[:-1]
            city = value["city"].strip()
            if city == "2142":
                city = value["settlement"]
            if location_name == "BMW Ste-Agathe":
                state = "QC"
            else:
                state = value["state"]
            zipp = value["postalCode"]
            if not zipp:
                zipp = "<MISSING>"
            country_code = value["countryCode"]
            phone = value["attributes"]["phone"].replace("+1 ", "")
            if not phone:
                phone = "<MISSING>"
            lat = value["lat"]
            lng = value["lng"]
            store_number = value["attributes"]["distributionPartnerId"]
            link = value["attributes"]["homepage"]
            if not link:
                if country_code == "US" and zipp != "<MISSING>":
                    try:
                        zip_api = "https://www.bmwusa.com/api/dealers/maco/" + zipp
                        zip_data = session.get(zip_api, headers=headers1).json()
                        if (
                            (zip_data["DealerCenterID"] == store_number)
                            or (zip_data["DealerAddress"] == value["street"])
                            or (zip_data["DealerName"] == value["name"])
                        ):
                            link = zip_data["DealerUrl"]
                    except:
                        pass
                else:
                    link = "<MISSING>"
                if not link:
                    link = "<MISSING>"

            if not state:
                if country_code == "US" and zipp != "<MISSING>":
                    try:
                        zip_api = "https://www.bmwusa.com/api/dealers/maco/" + zipp
                        zip_data = session.get(zip_api, headers=headers1).json()
                        if (
                            (zip_data["DealerCenterID"] == store_number)
                            or (zip_data["DealerAddress"] == value["street"])
                            or (zip_data["DealerName"] == value["name"])
                        ):
                            state = zip_data["DealerState"]
                    except:
                        pass
                else:
                    state = "<MISSING>"
                if not state:
                    state = "<MISSING>"

            if street_address + city + zipp in addresses:
                continue
            addresses.append(street_address + city + zipp)

            if street_address + city + store_number in addresses:
                continue
            addresses.append(street_address + city + store_number)

            if location_name + city + store_number in addresses:
                continue
            addresses.append(location_name + city + store_number)

            hours_of_operation = "<MISSING>"
            if country_code == "US":
                for us_loc in us_locs:
                    if (
                        (
                            us_loc["DefaultService"]["Name"].replace("amp;", "")
                            == location_name
                        )
                        or (
                            us_loc["Url"].strip().replace(".com/", ".com")
                            == link.replace(".com/", ".com")
                        )
                        or (us_loc["DefaultService"]["Address"] == street_address)
                    ):
                        try:
                            hours_of_operation = " ".join(
                                us_loc["DefaultService"]["Hours"]
                            )
                        except:
                            pass
                        break

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type="<MISSING>",
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(
    SgRecordDeduper(
        SgRecordID(
            {
                SgRecord.Headers.STREET_ADDRESS,
                SgRecord.Headers.LATITUDE,
                SgRecord.Headers.LONGITUDE,
                SgRecord.Headers.PHONE,
            }
        )
    )
) as writer:
    fetch_data(writer)
