from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

import ssl
from sgscrape import simple_utils as utils
from sgrequests.sgrequests import SgRequests
from requests.packages.urllib3.util.retry import Retry

from sgselenium import SgChrome

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.keys import Keys

from fuzzywuzzy import process

# no need for python-Levenshtein, we're processing only 30 records

import json  # noqa

import time

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def return_last4(fullId):
    last4 = list(fullId[-4:])
    while last4[0] == "0":
        last4.pop(0)
    return "".join(last4)


def _detStation(fullId, last4, defaultHeaders):
    determinationStation = {
        "Shop Easy Foods": {
            "url": "https://www.shopeasy.ca/find-store/?location={fullId}".format(
                fullId=fullId
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://www.shopeasy.ca/find-store/?location=LCL0063332
        # Full "ThirdPartyId"
        # api is bullseye https://ws2.bullseyelocations.com/RestSearch.svc/GetLocation?ClientId=4664&ApiKey=e5433c79-ae19-4247-af54-d32f8b9782fd&LanguageCode=en&ThirdPartyId=LCL0063332
        "Wellwise": {
            "url": "https://www.wellwise.ca/stores/store/{last4}".format(last4=last4),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://www.wellwise.ca/stores/store/8453
        # "ThirdPartyId": "SDM0008453", only last 4
        # no api in sight
        "Atlantic Superstore": {
            "url": "https://www.atlanticsuperstore.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "rass",
            },
            "api": "https://www.atlanticsuperstore.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        # https://www.atlanticsuperstore.ca/store-locator/details/0379
        # api : https://www.atlanticsuperstore.ca/api/pickup-locations/0379
        # "ThirdPartyId": "LCL0000379", only last 4
        "Zehrs": {
            "url": "https://www.zehrs.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "zehrs",
            },
            "api": "https://www.zehrs.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        # https://www.zehrs.ca/store-locator/details/0552
        # https://www.zehrs.ca/api/pickup-locations/0552
        # "ThirdPartyId": "LCL0000552", only last 4
        "Provigo Le Marché": {
            "url": "https://www.provigo.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "provigo",
            },
            "api": "https://www.provigo.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Provigo": {
            "url": "https://www.provigo.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "provigo",
            },
            "api": "https://www.provigo.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Independent City Market": {
            "url": "https://www.independentcitymarket.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "independentcitymarket",
            },
            "api": "https://www.independentcitymarket.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "L'Intermarche international": {
            "url": "https://www.marchepalumbo.com/en/locations",
            "headers": defaultHeaders,
            "api": None,
        },
        # https://www.marchepalumbo.com/en/store/519785/intermarche-palumbo
        # "ThirdPartyId": "LCL0068498", # noqa
        # Can't reconstruct URL from this, will have to blanket with
        # https://www.marchepalumbo.com/en/locations
        "PHARMAPRIX": {
            "url": "https://stores.pharmaprix.ca/en/store/{last4}".format(last4=last4),
            "headers": defaultHeaders,
            "api": None,
        },
        # SDM0001949
        # no api
        "Super Valu Foods": {
            "url": None,
            "headers": None,
            "api": None,
        },
        # hmmm really all locatioons in this category are 100% definitely missing..
        "Beauty Boutique By Shoppers": {
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(
                last4=last4
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://stores.shoppersdrugmart.ca/en/store/4022
        "Club Entrepôt": {
            "url": "https://www.wholesaleclub.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "wholesaleclub",
            },
            "api": "https://www.wholesaleclub.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        # https://www.wholesaleclub.ca/store-locator/details/8243
        # LCL0008243
        "Freshmart": {
            "url": "https://www.freshmart.ca/find-store/?location={fullId}".format(
                fullId=fullId
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://www.freshmart.ca/find-store/?location=LCL0052941
        "Joe": {
            "url": "https://www.joefresh.com/ca/store-locator",
            "headers": defaultHeaders,
            "api": None,
        },
        "L'Intermarche": {
            "url": "https://www.lintermarche.ca/trouver-un-magasin/?location={fullId}".format(
                fullId=fullId
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://www.lintermarche.ca/trouver-un-magasin/?location=LCL0030406
        "Shoppers Drug Mart": {
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(
                last4=last4
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://stores.shoppersdrugmart.ca/en/store/2002/
        "Real Canadian Liquorstore™": {
            "url": "https://www.realcanadianliquorstore.ca/find-location/?location={fullId}".format(
                fullId=fullId
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://www.realcanadianliquorstore.ca/find-location/?location=LCL0001645
        "Fortinos": {
            "url": "https://www.fortinos.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "fortinos",
            },
            "api": "https://www.fortinos.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Valu-mart": {
            "url": "https://www.valumart.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "valumart",
            },
            "api": "https://www.valumart.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Your Independent Grocer": {
            "url": "https://www.yourindependentgrocer.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "valumart",
            },
            "api": "https://www.yourindependentgrocer.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Maxi": {
            "url": "https://www.maxi.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "maxi",
            },
            "api": "https://www.maxi.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Wholesale Club": {
            "url": "https://www.wholesaleclub.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "wholesaleclub",
            },
            "api": "https://www.wholesaleclub.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Shoppers Simply Pharmacy": {
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(
                last4=last4
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        "Loblaws": {
            "url": "https://www.loblaws.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "loblaw",
            },
            "api": "https://www.loblaws.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Real Canadian Superstore": {
            "url": "https://www.realcanadiansuperstore.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "superstore",
            },
            "api": "https://www.realcanadiansuperstore.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Axep": {
            "url": "https://www.axep.ca/find-store/?location={fullId}".format(
                fullId=fullId
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        "Extra Foods": {
            "url": "https://www.extrafoods.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "extrafoods",
            },
            "api": "https://www.extrafoods.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "Dominion": {
            "url": "https://www.newfoundlandgrocerystores.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "dominion",
            },
            "api": "https://www.newfoundlandgrocerystores.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "HOME HEALTH CARE": {
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(
                last4=last4
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        # LAST 4 CAN NOT START WITH 0 !!!!
        # Addressed this
        # Has to start with 0 for a few..
        "No Frills": {
            "url": "https://www.nofrills.ca/store-locator/details/{last4}".format(
                last4=last4
            ),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "nofrills",
            },
            "api": "https://www.nofrills.ca/api/pickup-locations/{last4}".format(
                last4=last4
            ),
        },
        "SPECIALTY HEALTH NETWORK": {
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(
                last4=last4
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        "The Beauty Clinic By Shoppers": {
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(
                last4=last4
            ),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://stores.shoppersdrugmart.ca/en/store/6071
    }
    return determinationStation


def determine_verification_link(rec, typ, fullId, last4, typIter):
    defaultHeaders = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    determinationStation = _detStation(fullId, last4, defaultHeaders)

    def determined_possible():
        def passed():
            retryBehaviour = Retry(total=2, connect=2, read=2, backoff_factor=0.1)
            retryBehaviour = False
            with SgRequests(
                retry_behavior=retryBehaviour, proxy_rotation_failure_threshold=2
            ) as session:
                try:
                    if result["api"]:
                        test_url = result["api"]
                        test = SgRequests.raise_on_err(
                            session.get(test_url, headers=result["headers"])
                        ).json()
                    elif result["url"]:
                        test_url = result["url"]
                        test = SgRequests.raise_on_err(
                            session.get(test_url, headers=result["headers"])
                        ).json()
                    else:
                        test = None
                    if test:
                        if test.status_code != 404:
                            return test
                    return False
                except Exception as e:  # noqa
                    return False

        try:
            result = rec
            result.update({"type": typ[typIter].strip()})
            result.update(determinationStation[result["type"]])
            result.update({"passed": passed()})
            if result["passed"]:
                if not result["PhoneNumber"] or "one" in result["PhoneNumber"]:
                    if result["passed"]["contactNumber"]:
                        result["PhoneNumber"] = result["passed"]["contactNumber"]
                    else:
                        if result["passed"]["storeDetails"]["phoneNumber"]:
                            result["PhoneNumber"] = result["passed"]["storeDetails"][
                                "phoneNumber"
                            ]
                    result["passed"] = True
                    # cleaning this up.

            return result
        except Exception as e:  # noqa
            return None

    result = determined_possible()
    if result:
        return result
    else:
        if (typIter + 1) < len(typ):
            return determine_verification_link(rec, typ, fullId, last4, typIter + 1)
        else:
            return None


def do_everything(k):
    rec = k
    k.update({"megaFailed": False})
    typ = k["CategoryNames"].split(",")
    fullId = k["ThirdPartyId"]
    last4 = return_last4(fullId)
    k = determine_verification_link(rec, typ, fullId, str(last4), 0)
    # sometimes, if last4 starts with 0, they have to be all 4, most of the times, not.
    if k:
        if len(last4) != 4:
            if not k["passed"]:
                while len(last4) < 4:
                    last4 = "0" + str(last4)
                copyk = k
                k = determine_verification_link(rec, typ, fullId, str(last4), 0)
                if not k:
                    k = copyk
    if not k:
        if len(last4) != 4:
            while len(last4) < 4:
                last4 = "0" + str(last4)
        k = determine_verification_link(rec, typ, fullId, str(last4), 0)
        if k:
            return k
        k = rec
        k.update({"passed": False})
        k.update({"megaFailed": True})
    return k


def url_fix(url):
    url = url.split("StartIndex")[0] + "StartIndex" + "=0"
    url = "Radius=200".join(url.split("Radius="))  # (means 20020)
    url = "MaxResults=100".join(url.split("MaxResults="))  # (means 10010)
    url = "PageSize=100".join(url.split("PageSize="))  # (means 10010)
    return url


def get_api_call(url):
    driver = SgChrome().driver()
    driver.get(url)
    to_click = WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="root"]/section/div/div[1]/div[2]/div')
        )
    )
    to_click.click()

    input_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "/html/body/div[6]/div[3]/div[2]/section/div/div[1]/div[2]/div/div[3]/form/div/div[2]/div/input",
            )
        )
    )
    input_field.send_keys("B3L 4T2")
    input_field.send_keys(Keys.RETURN)
    time.sleep(10)
    wait_for_loc = WebDriverWait(driver, 30).until(  # noqa
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "/html/body/div[6]/div[3]/div[2]/section/div/div[3]/div[1]/div/ol/li[1]/div",
            )
        )
    )

    time.sleep(10)
    for r in driver.requests:
        if "DoSearch2" in r.path:
            url = r.url
            headers = r.headers
    driver.quit()
    time.sleep(10)
    return url, headers


def defuzz(record):
    knownTypes = [
        "Shop Easy Foods",
        "Wellwise",
        "Atlantic Superstore",
        "Zehrs",
        "Provigo Le Marché",
        "Provigo",
        "Independent City Market",
        "L'Intermarche international",
        "PHARMAPRIX",
        "Super Valu Foods",
        "Beauty Boutique By Shoppers",
        "Club Entrepôt",
        "Freshmart",
        "Joe",
        "L'Intermarche",
        "Shoppers Drug Mart",
        "Real Canadian Liquorstore™",
        "Fortinos",
        "Valu-mart",
        "Your Independent Grocer",
        "Maxi",
        "Wholesale Club",
        "Shoppers Simply Pharmacy",
        "Loblaws",
        "Real Canadian Superstore",
        "Axep",
        "Extra Foods",
        "Dominion",
        "HOME HEALTH CARE",
        "No Frills",
        "SPECIALTY HEALTH NETWORK",
        "The Beauty Clinic By Shoppers",
    ]
    # obtained by list(determinationStation) # noqa
    knownTypes = knownTypes
    testString = record["Name"] + "," + record["CategoryNames"]
    result = process.extractOne(testString, knownTypes)
    if result[1] > 50:
        record["ttype"] = result[0]
        record["CategoryNames"] = result[0] + ","
        return do_everything(record)
    else:
        raise record
    # if this ever becomes a problem print testString and result to debug.
    # if updating determinationStation please also update knownTypes. (sorry)
    # use the testing area in fetch_data()


def fix_phone(record):
    for attribute in record["Attributes"]:
        if "Phone" in attribute["AttributeName"]:
            return attribute["AttributeValue"]


def lesser_determination(banner, fullId):
    # "HOME HEALTH CARE": { # noqa
    #         "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format( # noqa
    #            last4=last4 # noqa
    #        ), # noqa
    #        "headers": defaultHeaders, # noqa
    #        "api": None, # noqa
    #    }, # noqa

    defaultHeaders = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    determinationStation = _detStation(fullId, fullId, defaultHeaders)

    for i in list(determinationStation):
        try:
            if (
                determinationStation[i]["headers"]["Site-Banner"] == banner
                or banner in determinationStation[i]["headers"]["Site-Banner"]
            ):
                return str(i), str(determinationStation[i]["url"])
        except Exception:
            pass


def lesser_datasource():
    url = "https://www.loblaws.ca/api/pickup-locations"
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    lesserData = SgRequests.raise_on_err(session.get(url, headers=headers)).json()
    session.close()
    for i in lesserData:
        loctype, url = lesser_determination(
            i["storeBannerId"], i["id"] if i["id"] else i["storeId"]
        )
        yield {
            "url": url,
            "Name": i["name"],
            "Latitude": i["geoPoint"]["latitude"],
            "Longitude": i["geoPoint"]["longitude"],
            "Address1": i["address"]["line1"],
            "Address2": i["address"]["line2"],
            "Address3": "",
            "Address4": "",
            "City": i["address"]["town"],
            "State": i["address"]["region"],
            "PostCode": i["address"]["postalCode"],
            "CountryCode": i["address"]["country"],
            "PhoneNumber": i["contactNumber"],
            "ThirdPartyId": i["id"] if i["id"] else i["storeId"],
            "BusinessHours": "",
            "ttype": loctype,
        }


def fetch_data():
    # https://ws2.bullseyelocations.com/RestSearch.svc/ # noqa
    # DoSearch2? # noqa
    # ClientId=4664 # noqa
    # ApiKey=27ab1bab-2901-4156-aec2-bfb51a7ce538 # noqa
    # Latitude=47.545417 # noqa
    # Longitude=-52.74302770000001 # noqa
    # Radius=20000 # noqa
    # SearchTypeOverride=1 # noqa
    # MaxResults=10000 # noqa
    # PageSize=10000 # noqa
    # StartIndex=0 # noqa

    # TESTING AREA: # noqa
    # (for records that megafailed) # noqa
    # rename megafails.txt to tofix.txt # noqa
    # ======== # noqa
    # with open('tofix.txt', mode='r', encoding = 'utf-8') as file: # noqa
    #    son = json.loads(file.read()) # noqa
    #    print(len(son)) # noqa
    # for i in son: # noqa
    #    if i["megaFailed"]: # noqa
    #        yield defuzz(i) # noqa
    # z = 1/0 # noqa
    # ======== # noqa

    url = "https://www.joefresh.com/ca/store-locator"
    # url entrypoint to get all loblaws data
    logzilla.info(f"Figuring out bullseye url and headers with selenium")  # noqa

    def rRetry(retry):
        def retry_starting():
            try:
                return get_api_call(url)
            except Exception as e:
                logzilla.info(f"Handling this:\n{str(e)}")
                retry_starting()
                # shouldn't be to worried,
                # worst case if their API changes crawl will timeout
                # rather than just pull from the other (worse) data source

        if retry:
            retry_starting()
        return get_api_call(url)

    url, headers = rRetry(False)
    logzilla.info(f"Found out this bullseye url:\n{url}\n\n& headers:\n{headers}")

    logzilla.info(f"Fixing up URL,")  # noqa
    url = url_fix(url)
    logzilla.info(f"New URL:\n{url}\n\n")

    session = SgRequests()
    headers = dict(headers)
    bullsEyeData = SgRequests.raise_on_err(session.get(url, headers=headers)).json()
    session.close()

    lize = utils.parallelize(
        search_space=bullsEyeData["ResultList"],
        fetch_results_for_rec=defuzz,
        max_threads=10,
        print_stats_interval=10,
    )
    megafails = []  # noqa
    # for i in bullsEyeData["ResultList"]: # noqa
    #    print('\n\n\nNew record:\n') # noqa
    #    res = do_everything(i) # noqa
    #    if res["megaFailed"]: # noqa
    #        print('definitely megafailed') # noqa
    #        megafails.append(res) # noqa
    for i in lize:
        if (
            not i["PhoneNumber"]
            or i["PhoneNumber"] == "null"
            or i["PhoneNumber"] == "none"
        ):
            i["PhoneNumber"] = fix_phone(i)
        if i["megaFailed"]:
            megafails.append(i)  # noqa
            yield defuzz(i)
        else:
            yield i

    # ########for debugging megafails: # noqa
    # print(len(megafails)) # noqa
    # with open('megafails.txt', mode='w', encoding = 'utf-8') as file: # noqa
    #    file.write(json.dumps(megafails)) # noqa

    for i in lesser_datasource():
        yield i
    logzilla.info(f"Finished grabbing data!!☺ ")  # noqa


def fix_comma(x):
    x = x.replace("null", "").replace("None", "")
    h = []
    try:
        for i in x.split(", "):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def fix_domain(x):
    try:
        return (
            "/".join(x.split("/")[:3])
            .replace("('None',)", "<MISSING>")
            .replace("'", "")
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .replace("None", "<MISSING>")
        )
    except Exception:
        return (
            x.replace("('None',)", "<MISSING>")
            .replace("'", "")
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .replace("None", "<MISSING>")
        )


def showme(x):
    logzilla.info(f"Showme: {x}")
    return x


def phoneident(x):
    phone = []
    for i in x:
        if i.isdigit():
            phone.append(i)
    x = "".join(phone)
    return x


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(
            mapping=["url"],
            value_transform=fix_domain,
            is_required=False,
        ),
        page_url=sp.MappingField(
            mapping=["url"],
            value_transform=lambda x: x.replace("('None',)", "<MISSING>").replace(
                "None", "<MISSING>"
            ),
            is_required=False,
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["Name"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["Latitude"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["Longitude"],
            is_required=False,
        ),
        street_address=sp.MultiMappingField(
            mapping=[["Address1"], ["Address2"], ["Address3"], ["Address4"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
            is_required=False,
        ),
        city=sp.MappingField(
            mapping=["City"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["State"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["PostCode"],
            value_transform=lambda x: x.replace(" ", "").strip(),
            is_required=False,
            part_of_record_identity=True,
        ),
        country_code=sp.MappingField(
            mapping=["CountryCode"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["PhoneNumber"],
            value_transform=phoneident,
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["ThirdPartyId"],
            is_required=False,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["BusinessHours"],
            is_required=False,
        ),
        location_type=sp.MappingField(
            mapping=["ttype"],
            is_required=False,
            part_of_record_identity=True,
        ),
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
