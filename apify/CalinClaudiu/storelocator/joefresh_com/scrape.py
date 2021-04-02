from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog


from sgscrape import simple_utils as utils

from sgrequests import SgRequests
from requests.packages.urllib3.util.retry import Retry

from sgselenium import SgFirefox

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.keys import Keys

import time
import json

def return_last4(fullId):
    if fullId[-4:][0]!='0':
        return fullId[-4:]
    return fullId[-3:]
    last4 = return_last4(fullId)

def determine_verification_link(rec, typ, fullId, last4, typIter):
    defaultHeaders = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    
    print('this is last4: ',last4)
    
    determinationStation = {
        "Shop Easy Foods": {
            "url": "https://www.shopeasy.ca/find-store/?location={fullId}".format(fullId=fullId),
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
            "url": "https://www.atlanticsuperstore.ca/store-locator/details/{last4}".format(last4=last4),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "rass",
            },
            "api": "https://www.atlanticsuperstore.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        # https://www.atlanticsuperstore.ca/store-locator/details/0379
        # api : https://www.atlanticsuperstore.ca/api/pickup-locations/0379
        # "ThirdPartyId": "LCL0000379", only last 4
        "Zehrs": {
            "url": "https://www.zehrs.ca/store-locator/details/{last4}".format(last4=last4),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "zehrs",
            },
            "api": "https://www.zehrs.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        # https://www.zehrs.ca/store-locator/details/0552
        # https://www.zehrs.ca/api/pickup-locations/0552
        # "ThirdPartyId": "LCL0000552", only last 4
        "Provigo Le Marché": {
            "url": "https://www.provigo.ca/store-locator/details/{last4}".format(last4=last4),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "provigo",
            },
            "api": "https://www.provigo.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        "Provigo": {
            "url": "https://www.provigo.ca/store-locator/details/{last4}".format(last4=last4),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "provigo",
            },
            "api": "https://www.provigo.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        "Independent City Market": {
            "url": "https://www.independentcitymarket.ca/store-locator/details/{last4}".format(last4=last4),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "independentcitymarket",
            },
            "api": "https://www.independentcitymarket.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        "L'Intermarche international": {
            "url": "https://www.marchepalumbo.com/en/locations",
            "headers": defaultHeaders,
            "api": None,
        },
        # https://www.marchepalumbo.com/en/store/519785/intermarche-palumbo
        # "ThirdPartyId": "LCL0068498",
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
        "Beauty Boutique By Shoppers": {
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(last4=last4),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://stores.shoppersdrugmart.ca/en/store/4022
        "Club Entrepôt": {
            "url": "https://www.wholesaleclub.ca/store-locator/details/{last4}".format(last4=last4),
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "wholesaleclub",
            },
            "api": "https://www.wholesaleclub.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        # https://www.wholesaleclub.ca/store-locator/details/8243
        # LCL0008243
        "Freshmart": {
            "url": "https://www.freshmart.ca/find-store/?location=".format(fullId=fullId),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://www.freshmart.ca/find-store/?location=LCL0052941
        "Joe": {
            "url": "https://www.joefresh.com/ca/store-locator",
            "headers": defaultHeaders,
            "api": None,
        },
        "Regions - LCL": {
            "url": None,
            "headers": None,
            "api": None,
        },
        "L'Intermarche": {
            "url": "https://www.lintermarche.ca/trouver-un-magasin/?location=".format(fullId=fullId),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://www.lintermarche.ca/trouver-un-magasin/?location=LCL0030406
        "Shoppers Drug Mart": {
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(last4=last4),
            "headers": defaultHeaders,
            "api": None,
        },
        # https://stores.shoppersdrugmart.ca/en/store/2002/

        "Real Canadian Liquorstore™":{
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(last4=last4),
            "headers": defaultHeaders,
            "api": None,
        },

        "Fortinos":{
            "url":"https://www.fortinos.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "fortinos",
            },
            "api": "https://www.fortinos.ca/api/pickup-locations/{last4}".format(last4=last4),
        },

        "Valu-mart":{
            "url":"https://www.valumart.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "valumart",
            },
            "api": "https://www.valumart.ca/api/pickup-locations/{last4}".format(last4=last4),
        },

        "Your Independent Grocer":{
            "url":"https://www.yourindependentgrocer.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "valumart",
            },
            "api": "https://www.yourindependentgrocer.ca/api/pickup-locations/{last4}".format(last4=last4),
        },

        "Maxi":{
            "url":"https://www.maxi.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "maxi",
            },
            "api": "https://www.maxi.ca/api/pickup-locations/{last4}".format(last4=last4),
        },

        'Wholesale Club':{
            "url":"https://www.wholesaleclub.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "wholesaleclub",
            },
            "api": "https://www.wholesaleclub.ca/api/pickup-locations/{last4}".format(last4=last4),
        },

        'Shoppers Simply Pharmacy':{
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(last4=last4),
            "headers": defaultHeaders,
            "api": None,
        },

        'Loblaws':{
            "url":"https://www.loblaws.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "loblaw",
            },
            "api": "https://www.loblaws.ca/api/pickup-locations/{last4}".format(last4=last4),
        },

        'Real Canadian Superstore':{
            "url":"https://www.realcanadiansuperstore.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "superstore",
            },
            "api": "https://www.realcanadiansuperstore.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        "Axep": {
            "url": "https://www.axep.ca/find-store/?location=".format(fullId=fullId),
            "headers": defaultHeaders,
            "api": None,
        },

        'Extra Foods':{
            "url":"https://www.extrafoods.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "extrafoods",
            },
            "api": "https://www.extrafoods.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        'Dominion':{
            "url":"https://www.newfoundlandgrocerystores.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "dominion",
            },
            "api": "https://www.newfoundlandgrocerystores.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        'HOME HEALTH CARE':{
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(last4=last4),
            "headers": defaultHeaders,
            "api": None,
        },
        # LAST 4 CAN NOT START WITH 0 !!!!
        # Addressed this :)
        # Has to start with 0 for a few..
        'No Frills':{
            "url":"https://www.yourindependentgrocer.ca/store-locator/details/{last4}".format(last4=last4),
            "headers":{
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "Site-Banner": "nofrills",
            },
            "api": "https://www.yourindependentgrocer.ca/api/pickup-locations/{last4}".format(last4=last4),
        },
        'SPECIALTY HEALTH NETWORK':{
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(last4=last4),
            "headers": defaultHeaders,
            "api": None,
        },
        'The Beauty Clinic By Shoppers':{
            "url": "https://stores.shoppersdrugmart.ca/en/store/{last4}".format(last4=last4),
            "headers": defaultHeaders,
            "api": None,
        },
        #https://stores.shoppersdrugmart.ca/en/store/6071
        }
    def determined_possible():
        def passed():
            retryBehaviour = Retry(total=2, connect=2, read=2, backoff_factor=0.1)
            retryBehaviour = False
            with SgRequests(retry_behavior=retryBehaviour,  proxy_rotation_failure_threshold = 2) as session:
                try:
                    if result["api"]:
                        test_url = result["api"]
                        print(test_url)
                        test = session.get(test_url, headers = result["headers"])
                    elif result["url"]:
                        test_url = result["url"]
                        print(test_url)
                        test = session.get(test_url, headers = result["headers"])
                    else:
                        test = None
                    print("Test length: ",len(test.text))
                    if test:
                        if test.status_code!=404:
                            print('passed -> ',test.status_code,' returning True')
                            return True
                        else:
                            print('\n','\napi:',result["api"],'\nurl:',test['url'])
                            print(test.status_code)
                    return False
                except Exception as e:
                    print('Exception is:\n',e,'\n\nWith details:\n','\napi:',result["api"],'\nurl:',test['url'],'\n')
                    return False
            
        try:
            result = rec
            result.update({'type':typ[typIter].strip()})
            result.update(determinationStation[result['type']])
            result.update({'passed':passed()})
            print('In try passed: ',result['passed'])
            return result
        except Exception as e:
            print('For type: ',result['type'],'\n\nThis is the exception: ',str(e))
            return None

    result = determined_possible()
    if result:
        return result
    else:
        if (typIter+1)<len(typ):
            print('trying next: ',typ[typIter+1],' after failing this: ',typ[typIter])
            return determine_verification_link(rec, typ, fullId, last4, typIter+1)
            print('MegaFailed inside!!\n',typ,'\n',typIter,' len: ',len(typ))
            return None

    
def do_everything(k):
    rec = k
    k.update({'megaFailed':False})
    typ = k["CategoryNames"].split(",")
    fullId = k["ThirdPartyId"]
    last4 = return_last4(fullId)
    k = determine_verification_link(rec, typ, fullId, last4, 0)
    #sometimes, if last4 starts with 0, they have to be all 4, most of the times, not.
    if k:
        if len(last4)==3 and not k['passed']:
            print('GOT In IF?!?===============')
            copyk = k
            k = determine_verification_link(rec, typ, fullId, '0'+str(last4), 0)
            if not k:
                k = copyk
    if not k:
        k = determine_verification_link(rec, typ, fullId, '0'+str(last4), 0)
        if k:
            return k
        k = rec
        k.update({'megaFailed':True})
        print('MegaFailed')
    return k

def url_fix(url):
    url = url.split("StartIndex")[0] + "StartIndex" + "=0"
    url = "Radius=200".join(url.split("Radius="))
    url = "MaxResults=100".join(url.split("MaxResults="))
    url = "PageSize=100".join(url.split("PageSize="))
    return url

def get_api_call(url):
    with SgFirefox() as driver:
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
                    "/html/body/div[6]/div[3]/div[2]/section/div/div[1]/div[2]/div/div[2]/form/div[1]/div[2]/input",
                )
            )
        )
        input_field.send_keys("B3L 4T2")
        input_field.send_keys(Keys.RETURN)

        wait_for_loc = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[6]/div[3]/div[2]/section/div/div[3]/div[1]/div/ol/li[1]/div",
                )
            )
        )
        for r in driver.requests:
            if "DoSearch2" in r.path:
                url = r.url
                headers = r.headers

    return url, headers



def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    # https://ws2.bullseyelocations.com/RestSearch.svc/
    # DoSearch2?
    # ClientId=4664
    # ApiKey=27ab1bab-2901-4156-aec2-bfb51a7ce538
    # Latitude=47.545417
    # Longitude=-52.74302770000001
    # Radius=20000
    # SearchTypeOverride=1
    # MaxResults=10000
    # PageSize=10000
    # StartIndex=0

    url = "https://www.joefresh.com/ca/store-locator"

    logzilla.info(f"Figuring out bullseye url and headers with selenium")  # noqa
    url, headers = get_api_call(url)
    logzilla.info(f"Found out this bullseye url:\n{url}\n\n& headers:\n{headers}")

    logzilla.info(f"Fixing up URL")  # noqa
    url = url_fix(url)
    logzilla.info(f"New URL:\n{url}\n\n")

    session = SgRequests()
    bullsEyeData = session.get(url, headers=headers).json()
    session.close()
    
    lize = utils.parallelize(
        search_space=bullsEyeData["ResultList"],
        fetch_results_for_rec=do_everything,
        max_threads=10,
        print_stats_interval=50,
    )
    megafails = []
    for i in bullsEyeData["ResultList"]:
        print('\n\n\nNew record:\n')
        res = do_everything(i)
        if res["megaFailed"]:
            print('definitely megafailed')
            megafails.append(res)
    #for i in lize:
    #    yield i
    #    if i["megaFailed"]:
    #        print('definitely megafailed')
    #        megafails.append(i)

    for i in megafails:
        print(i)
    print(len(megafails))
    with open('megafails.txt', mode='w', encoding = 'utf-8') as file:
        file.write(json.dumps(megafails))

            
    logzilla.info(f"Finished grabbing data!!☺ ")

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
        return '/'.join(x.split('/')[:3]),
    except Exception:
        return x.replace('none',"<MISSING>").replace('None',"<MISSING>")
        
def scrape():
    url = "joefreshAPI"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(
            mapping=["url"],
            is_required=False,
        ),
        page_url=sp.MappingField(
            mapping=["url"],
            value_transform = lambda x : x.replace('None','<MISSING>'),
            is_required=False,
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
            is_required=False,
        ),
        country_code=sp.MappingField(
            mapping=["CountryCode"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["PhoneNumber"],
            value_transform = lambda x : x.replace('none',"<MISSING>").replace('None',"<MISSING>"),
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
            mapping=['type'],
            is_required=False,
        ),
        raw_address=sp.MappingField(
            mapping=['passed'],
            is_required=False,
        ),
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
