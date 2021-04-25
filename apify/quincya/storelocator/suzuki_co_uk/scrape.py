import csv
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests


log = sglog.SgLogSetup().get_logger(logger_name="suzuki.co.uk")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://cars.suzuki.co.uk/find-a-dealer/"
    api_link = "https://cars.suzuki.co.uk/DealerLookup/GetResults"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    get_headers = {"User-Agent": user_agent}

    headers = {
        "authority": "cars.suzuki.co.uk",
        "method": "POST",
        "path": "/DealerLookup/GetResults",
        "scheme": "https",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "30348",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": "OptanonAlertBoxClosed=2021-04-02T05:46:51.893Z; __RequestVerificationToken=atE0F7ToqnwJh0II1rHenXvyl7hbDSAWqzWjWZs0fe0E3vbzz-BnP0g1WGp6WodlbjH2Ausm7fMT5aapzROrx0Ts5nw1; OptanonConsent=isIABGlobal=false&datestamp=Wed+Apr+14+2021+04%3A13%3A21+GMT-0400+(Atlantic+Standard+Time)&version=5.12.0&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0%2CC0005%3A0&hosts=&geolocation=%3B&AwaitingReconsent=false; _bmap_dcm_dat=1; AMP_TOKEN=%24NOT_FOUND; ai_user=Otd4z|2021-04-02T05:46:45.590Z; _gcl_au=1.1.32205979.1617342406; _gat_UA-87934784-2=1; _gat_UA-87934784-9=1; _hjTLDTest=1; _hjid=d2ebd30f-1bc9-477e-bb34-842ec807dd68; _hjFirstSeen=1; _fbp=fb.2.1617342407283.773316268; _hjAbsoluteSessionInProgress=1; __qca=P0-108603648-1617342407799; talkative_customer_journey_initial_time=1617342408275; talkative_qos_bandwidth=8.25; _gat_UA-87934784-7=1; _gat_False=1; _gid=GA1.3.733868799.1618208034; _hjIncludedInPageviewSample=1; _hjIncludedInSessionSample=1; __fs_dncs_sessionid_suzukigb=6fcc122e-f8aa-48ed-9c0c-4187cd00908b; __fs_dncs_trackingid_suzukigb=e17ddbbc-d5ab-4106-a612-052b98ec1dae; __fs_dncs_exttrack=1; _ga=GA1.3.1074687389.1617339257; _uetsid=cf7a7350937611eba7c637a722448927; _uetvid=cf7ae640937611ebbcb9b963109d826c; ai_session=e7HEu|1618386947620|1618388003472.725; __fs_dncs_trackingid_suzukigb=e17ddbbc-d5ab-4106-a612-052b98ec1dae; __fs_dncs_exttrack=1; _hjIncludedInPageviewSample=1; _hjIncludedInSessionSample=1; _ga_C3VYEQGEQR=GS1.1.1618386944.12.1.1618389700.0; __fs_dncs_sessionid_suzukigb=6fcc122e-f8aa-48ed-9c0c-4187cd00908b; ai_session=gtLZj|1618431604655.54|1618431895066.25",
        "origin": "https://cars.suzuki.co.uk",
        "referer": "https://cars.suzuki.co.uk/find-a-dealer/",
        "request-context": "appId=cid-v1:8770dcd3-033a-4276-aecf-5dc894b630b1",
        "request-id": "|i35KK.doqgb",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    session = SgRequests()

    dup_tracker = []
    loc_data = []

    locator_domain = "suzuki.co.uk"

    req = session.get(base_link, headers=get_headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "allDealers" in str(script):
            script = str(script)
            break

    stores = json.loads(script.split("allDealers =")[1].split(";\r\n</sc")[0])

    for row in stores:
        dnum = row["dealerNumber"]
        dist = row["distance"]
        lat = row["location"]["lat"]
        lng = row["location"]["lng"]

        loc_data.append([dnum, dist, lat, lng])

    for i, row in enumerate(loc_data):
        dnum = row[0]
        dist = row[1]
        lat = row[2]
        lng = row[3]
        log.info("Searching: %s %s | %s of %s" % (lat, lng, i + 1, str(len(loc_data))))

        pay_data = (
            dnum
            + "%22%2C%22distance%22%3A"
            + str(dist)
            + "%2C%22location%22%3A%7B%22lat%22%3A"
            + str(lat)
            + "%2C%22lng%22%3A"
            + str(lng)
        )
        start_payload = "__RequestVerificationToken=0KxuErJ0f8r6teyKIPmXZXCcSD-M_nHzgDsPJHt3lyEiA5OtF4MQNJNnwO_uKdgcElbbcPXoE0o4O37IBdL9z0SUxpQ1&currentSite=Cars&dealerFolder=d4cbef28-ae7a-48c0-9b7a-b1d9bba9abfa&orderedDealerList=%5B%7B%22dealerNumber%22%3A%22"

        mid_payload = "%7D%7D%2C%7B%22dealerNumber%22%3A%22ba0f3a76-42fb-49ab-8d46-38215a90ebb7%22%2C%22distance%22%3A1.3605849035782986%2C%22location%22%3A%7B%22lat%22%3A51.908866%2C%22lng%22%3A-0.66011523%7D%7D%2C%7B%22dealerNumber%22%3A%2251792352-b2c8-421e-8e08-3ad2e1a213d4%22%2C%22distance%22%3A18556.17488609952%2C%22location%22%3A%7B%22lat%22%3A51.7789977%2C%22lng%22%3A-0.4909347%7D%7D%2C%7B%22dealerNumber%22%3A%225defe402-bcc3-4796-baaa-2e4bd5829f43%22%2C%22distance%22%3A20296.351221872268%2C%22location%22%3A%7B%22lat%22%3A52.06257%2C%22lng%22%3A-0.81932%7D%7D%2C%7B%22dealerNumber%22%3A%2289f03eae-d746-4f61-a6e7-d919377d88c8%22%2C%22distance%22%3A30394.24498221964%2C%22location%22%3A%7B%22lat%22%3A52.16395%2C%22lng%22%3A-0.5018749%7D%7D%2C%7B%22dealerNumber%22%3A%22f3801a7e-e544-4c2d-a449-92394c57cf89%22%2C%22distance%22%3A30914.98929445057%2C%22location%22%3A%7B%22lat%22%3A51.6371602%2C%22lng%22%3A-0.7530515%7D%7D%2C%7B%22dealerNumber%22%3A%220d5d51aa-b91b-45ae-84f3-c328ef7d8102%22%2C%22distance%22%3A31341.03002859532%2C%22location%22%3A%7B%22lat%22%3A51.9845088%2C%22lng%22%3A-0.2201533%7D%7D%2C%7B%22dealerNumber%22%3A%22843c02c1-97eb-482b-b6db-17b16ccca21c%22%2C%22distance%22%3A34342.909482185314%2C%22location%22%3A%7B%22lat%22%3A51.650197%2C%22lng%22%3A-0.38832889%7D%7D%2C%7B%22dealerNumber%22%3A%2258f43c74-5485-4d41-9f7b-a15a1832d516%22%2C%22distance%22%3A43764.57413279793%2C%22location%22%3A%7B%22lat%22%3A52.2771031%2C%22lng%22%3A-0.8842019%7D%7D%2C%7B%22dealerNumber%22%3A%22a4a0031d-93ad-4345-9e9c-01a73d7277bf%22%2C%22distance%22%3A44816.34729147594%2C%22location%22%3A%7B%22lat%22%3A51.514899%2C%22lng%22%3A-0.79397367%7D%7D%2C%7B%22dealerNumber%22%3A%220deef5cc-9e14-4763-aa64-348e9a14d234%22%2C%22distance%22%3A45744.481166641264%2C%22location%22%3A%7B%22lat%22%3A51.586097%2C%22lng%22%3A-0.24929597%7D%7D%2C%7B%22dealerNumber%22%3A%2238c25c29-4985-4e3a-b5cc-deac0cafa007%22%2C%22distance%22%3A46176.76460369982%2C%22location%22%3A%7B%22lat%22%3A51.5831816%2C%22lng%22%3A-0.2451513%7D%7D%2C%7B%22dealerNumber%22%3A%220a594f3a-1927-4d19-b8e4-52b88458585b%22%2C%22distance%22%3A51733.85330164221%2C%22location%22%3A%7B%22lat%22%3A51.825027%2C%22lng%22%3A-1.4003849%7D%7D%2C%7B%22dealerNumber%22%3A%22524cd9c1-99a3-4cfc-8b28-8b846a0c9b8c%22%2C%22distance%22%3A56151.98877262075%2C%22location%22%3A%7B%22lat%22%3A51.4440183%2C%22lng%22%3A-0.9759983%7D%7D%2C%7B%22dealerNumber%22%3A%220def942c-1bce-4bed-92b7-ac6273e1d0e0%22%2C%22distance%22%3A56720.76806524025%2C%22location%22%3A%7B%22lat%22%3A51.839945%2C%22lng%22%3A0.15761527%7D%7D%2C%7B%22dealerNumber%22%3A%22123fcbea-95f0-4925-957c-4053e90949aa%22%2C%22distance%22%3A56770.188470498746%2C%22location%22%3A%7B%22lat%22%3A51.6308448%2C%22lng%22%3A0.0307812%7D%7D%2C%7B%22dealerNumber%22%3A%229328b657-b932-412c-94f9-057eadf316eb%22%2C%22distance%22%3A64770.10134383086%2C%22location%22%3A%7B%22lat%22%3A52.490454%2C%22lng%22%3A-0.6873747%7D%7D%2C%7B%22dealerNumber%22%3A%22d19ec61b-c697-43a7-89e3-4373aa6b2bf5%22%2C%22distance%22%3A66401.7569212503%2C%22location%22%3A%7B%22lat%22%3A52.2122191%2C%22lng%22%3A0.1752457%7D%7D%2C%7B%22dealerNumber%22%3A%2230de65c8-6879-467d-9481-9d51e5fb5ba5%22%2C%22distance%22%3A67217.01632923148%2C%22location%22%3A%7B%22lat%22%3A52.385579%2C%22lng%22%3A-1.2640391%7D%7D%2C%7B%22dealerNumber%22%3A%22d35810a8-8810-4839-81d9-3e6420ed29a4%22%2C%22distance%22%3A68313.8903029384%2C%22location%22%3A%7B%22lat%22%3A51.574207%2C%22lng%22%3A0.17063737%7D%7D%2C%7B%22dealerNumber%22%3A%223583e675-9cf8-44e1-a313-de0b9f755d03%22%2C%22distance%22%3A73356.89557758167%2C%22location%22%3A%7B%22lat%22%3A51.460828%2C%22lng%22%3A0.11934384%7D%7D%2C%7B%22dealerNumber%22%3A%223c36cc7f-d250-4771-b8c5-50ad09455599%22%2C%22distance%22%3A73646.01591340362%2C%22location%22%3A%7B%22lat%22%3A51.267682%2C%22lng%22%3A-0.39771%7D%7D%2C%7B%22dealerNumber%22%3A%22a5e8834f-c61f-474d-a9a1-485ab7456462%22%2C%22distance%22%3A73990.43062681876%2C%22location%22%3A%7B%22lat%22%3A51.245438%2C%22lng%22%3A-0.72570139%7D%7D%2C%7B%22dealerNumber%22%3A%221ec9d0e1-bcd2-4f83-bbec-9e02bfa2ab42%22%2C%22distance%22%3A74747.11811911076%2C%22location%22%3A%7B%22lat%22%3A51.392548%2C%22lng%22%3A0.031808545%7D%7D%2C%7B%22dealerNumber%22%3A%22b9b86a7c-c790-4871-b1f7-d97579eaf421%22%2C%22distance%22%3A75837.24651810329%2C%22location%22%3A%7B%22lat%22%3A52.37835%2C%22lng%22%3A-1.4645229%7D%7D%2C%7B%22dealerNumber%22%3A%222d264306-4510-4196-9946-a0dd885902ac%22%2C%22distance%22%3A79699.65571710584%2C%22location%22%3A%7B%22lat%22%3A52.2014524%2C%22lng%22%3A-1.7227893%7D%7D%2C%7B%22dealerNumber%22%3A%2212abf75a-88fc-476c-a7c3-e8c67d04ad5c%22%2C%22distance%22%3A79850.37368064238%2C%22location%22%3A%7B%22lat%22%3A52.573305%2C%22lng%22%3A-0.21875105%7D%7D%2C%7B%22dealerNumber%22%3A%2227c2abb0-f6f9-4356-bf64-6bb6938a5029%22%2C%22distance%22%3A84770.86643053392%2C%22location%22%3A%7B%22lat%22%3A52.432778%2C%22lng%22%3A0.24097878%7D%7D%2C%7B%22dealerNumber%22%3A%22f1a621f2-9e5e-4635-8f7a-370950eb70e5%22%2C%22distance%22%3A84869.88832460147%2C%22location%22%3A%7B%22lat%22%3A51.4474201%2C%22lng%22%3A0.3186648%7D%7D%2C%7B%22dealerNumber%22%3A%22e0118aea-ed5e-42cb-b255-e1f5e51fb388%22%2C%22distance%22%3A85181.99655946063%2C%22location%22%3A%7B%22lat%22%3A51.164499%2C%22lng%22%3A-0.94532355%7D%7D%2C%7B%22dealerNumber%22%3A%22c4a463b5-197b-48b6-a4a5-25298d17b1f0%22%2C%22distance%22%3A85356.95072444249%2C%22location%22%3A%7B%22lat%22%3A52.61727%2C%22lng%22%3A-1.1395305%7D%7D%2C%7B%22dealerNumber%22%3A%223a51e117-0c0c-4309-acbd-a1f04588eff9%22%2C%22distance%22%3A88195.79770022168%2C%22location%22%3A%7B%22lat%22%3A51.558982%2C%22lng%22%3A-1.8079145%7D%7D%2C%7B%22dealerNumber%22%3A%226e259e29-5ca6-477a-98a9-64e922474e7d%22%2C%22distance%22%3A92314.96494457584%2C%22location%22%3A%7B%22lat%22%3A51.704997%2C%22lng%22%3A-1.9601712%7D%7D%2C%7B%22dealerNumber%22%3A%228c2509c0-b3cf-4288-a485-e220a23c720a%22%2C%22distance%22%3A93173.64862459972%2C%22location%22%3A%7B%22lat%22%3A51.7224674%2C%22lng%22%3A0.6598486%7D%7D%2C%7B%22dealerNumber%22%3A%2232b37f62-c120-4a7e-8822-a6fb673dfdd5%22%2C%22distance%22%3A95027.27733987517%2C%22location%22%3A%7B%22lat%22%3A52.311023%2C%22lng%22%3A-1.8861844%7D%7D%2C%7B%22dealerNumber%22%3A%22798a7aeb-a4c2-4fe1-b2ae-4172153a5db9%22%2C%22distance%22%3A96718.14491891346%2C%22location%22%3A%7B%22lat%22%3A52.766707%2C%22lng%22%3A-0.88548723%7D%7D%2C%7B%22dealerNumber%22%3A%22e4196b3c-fcb0-4164-bca0-6a42669241a6%22%2C%22distance%22%3A97371.70694262249%2C%22location%22%3A%7B%22lat%22%3A51.877264%2C%22lng%22%3A-2.07658%7D%7D%2C%7B%22dealerNumber%22%3A%22eadc3651-ac26-4f4a-a7e9-06ac96900c24%22%2C%22distance%22%3A101524.33587615349%2C%22location%22%3A%7B%22lat%22%3A51.557692%2C%22lng%22%3A0.69897323%7D%7D%2C%7B%22dealerNumber%22%3A%2278983d14-0a70-4f2c-9b99-0537987bd1ef%22%2C%22distance%22%3A103400.03251105097%2C%22location%22%3A%7B%22lat%22%3A52.241377%2C%22lng%22%3A0.75101952%7D%7D%2C%7B%22dealerNumber%22%3A%22db14a047-61b1-484a-9fc0-ce76de7acedf%22%2C%22distance%22%3A107005.80337706789%2C%22location%22%3A%7B%22lat%22%3A51.139476%2C%22lng%22%3A-1.5863189%7D%7D%2C%7B%22dealerNumber%22%3A%22ba5b34d7-2cd3-48c1-b0dd-e915396d96d4%22%2C%22distance%22%3A107084.54039439424%2C%22location%22%3A%7B%22lat%22%3A51.136541%2C%22lng%22%3A0.2616464%7D%7D%2C%7B%22dealerNumber%22%3A%2237a5f76a-c40c-4bef-80ea-48918f34773d%22%2C%22distance%22%3A107648.08831900035%2C%22location%22%3A%7B%22lat%22%3A50.99326%2C%22lng%22%3A-0.16078923%7D%7D%2C%7B%22dealerNumber%22%3A%22ebd6a116-c8c2-425f-86f8-d79a74c1608d%22%2C%22distance%22%3A108437.26842108028%2C%22location%22%3A%7B%22lat%22%3A52.534245%2C%22lng%22%3A-1.8792765%7D%7D%2C%7B%22dealerNumber%22%3A%2230db8972-281b-4f92-9df4-7a980e9e06af%22%2C%22distance%22%3A109351.66672284866%2C%22location%22%3A%7B%22lat%22%3A51.876024%2C%22lng%22%3A0.93076782%7D%7D%2C%7B%22dealerNumber%22%3A%22130e532c-4d2f-4566-816b-df96d7bbdd14%22%2C%22distance%22%3A110179.2813951686%2C%22location%22%3A%7B%22lat%22%3A52.160486%2C%22lng%22%3A-2.2161613%7D%7D%2C%7B%22dealerNumber%22%3A%22d8cd8880-fe6d-49a1-af56-a8363e11a8af%22%2C%22distance%22%3A112491.37290434046%2C%22location%22%3A%7B%22lat%22%3A51.2410585%2C%22lng%22%3A0.5602832%7D%7D%2C%7B%22dealerNumber%22%3A%2263f09567-049d-4f21-92fb-5283d32ca70c%22%2C%22distance%22%3A112826.3272100102%2C%22location%22%3A%7B%22lat%22%3A52.458925%2C%22lng%22%3A-2.0485813%7D%7D%2C%7B%22dealerNumber%22%3A%22942404b9-fa59-48d5-8a45-a81ce96c7ef0%22%2C%22distance%22%3A118789.35454187587%2C%22location%22%3A%7B%22lat%22%3A50.91576%2C%22lng%22%3A-1.28621%7D%7D%2C%7B%22dealerNumber%22%3A%225d7dac0e-7b8e-48e9-87c6-ce128668d16b%22%2C%22distance%22%3A119442.29156225982%2C%22location%22%3A%7B%22lat%22%3A50.848494%2C%22lng%22%3A-0.39733368%7D%7D%2C%7B%22dealerNumber%22%3A%2217d1a648-712f-4795-b55b-3df6b5da97ba%22%2C%22distance%22%3A119698.61543036811%2C%22location%22%3A%7B%22lat%22%3A50.854024%2C%22lng%22%3A-0.99446305%7D%7D%2C%7B%22dealerNumber%22%3A%2275c42c6b-bfce-40e1-a70a-13c26100c9ec%22%2C%22distance%22%3A120183.32985217818%2C%22location%22%3A%7B%22lat%22%3A52.372584%2C%22lng%22%3A-2.2487619%7D%7D%2C%7B%22dealerNumber%22%3A%2211c333e7-5a35-4413-8b93-45534a91c09a%22%2C%22distance%22%3A120336.85404408343%2C%22location%22%3A%7B%22lat%22%3A52.565961%2C%22lng%22%3A-2.0618302%7D%7D%2C%7B%22dealerNumber%22%3A%222a8e0c64-f7e1-47a0-bc25-692235c24045%22%2C%22distance%22%3A122266.58961909417%2C%22location%22%3A%7B%22lat%22%3A50.8409453%2C%22lng%22%3A-0.2487649%7D%7D%2C%7B%22dealerNumber%22%3A%2214f5f89f-9783-49bc-a9fb-88b3ec33ac7a%22%2C%22distance%22%3A122909.09347823367%2C%22location%22%3A%7B%22lat%22%3A51.0700525%2C%22lng%22%3A-1.8132432%7D%7D%2C%7B%22dealerNumber%22%3A%22a9af9af3-96bd-4b94-ade8-df35870dca13%22%2C%22distance%22%3A124238.47775443757%2C%22location%22%3A%7B%22lat%22%3A50.917911%2C%22lng%22%3A-1.4833701%7D%7D%2C%7B%22dealerNumber%22%3A%2202c153b6-26f7-4da7-a831-0c1de79bffaf%22%2C%22distance%22%3A124359.42910910139%2C%22location%22%3A%7B%22lat%22%3A52.980926%2C%22lng%22%3A-1.1754885%7D%7D%2C%7B%22dealerNumber%22%3A%221d3807f1-6947-4ef2-bb01-5cd0e52f58a4%22%2C%22distance%22%3A124429.42721856244%2C%22location%22%3A%7B%22lat%22%3A50.8404523%2C%22lng%22%3A-1.1864344%7D%7D%2C%7B%22dealerNumber%22%3A%22382fd168-b51f-4997-90b9-fff281f5c2c7%22%2C%22distance%22%3A124549.83420051103%2C%22location%22%3A%7B%22lat%22%3A51.332588%2C%22lng%22%3A-2.2048488%7D%7D%2C%7B%22dealerNumber%22%3A%22b721b588-a6ec-4dd8-bb4a-e6b847b286e3%22%2C%22distance%22%3A125142.04122502073%2C%22location%22%3A%7B%22lat%22%3A52.919583%2C%22lng%22%3A-1.4670056%7D%7D%2C%7B%22dealerNumber%22%3A%221280cffc-088d-4bc8-af64-48ee1b3e7eb4%22%2C%22distance%22%3A126355.80988612656%2C%22location%22%3A%7B%22lat%22%3A52.678625%2C%22lng%22%3A-2.024081%7D%7D%2C%7B%22dealerNumber%22%3A%22922ae011-ff9d-470e-8571-34a4dfcf786b%22%2C%22distance%22%3A128885.57645095723%2C%22location%22%3A%7B%22lat%22%3A53.005326%2C%22lng%22%3A-0.049870085%7D%7D%2C%7B%22dealerNumber%22%3A%224a9f76c5-94cf-49b3-a28d-5f0475d18f8d%22%2C%22distance%22%3A130522.56263089344%2C%22location%22%3A%7B%22lat%22%3A52.027145%2C%22lng%22%3A1.2333383%7D%7D%2C%7B%22dealerNumber%22%3A%2230b5838c-4c87-4f59-8bee-730e94b406f7%22%2C%22distance%22%3A134970.55500832497%2C%22location%22%3A%7B%22lat%22%3A51.7894501%2C%22lng%22%3A-2.613385%7D%7D%2C%7B%22dealerNumber%22%3A%2203f9f1c9-ede6-4c41-a07e-1667af14a130%22%2C%22distance%22%3A138308.02047514537%2C%22location%22%3A%7B%22lat%22%3A51.476121%2C%22lng%22%3A-2.5390091%7D%7D%2C%7B%22dealerNumber%22%3A%2210db7ce9-6448-472f-85ac-971b4f6d90f6%22%2C%22distance%22%3A138366.06257267558%2C%22location%22%3A%7B%22lat%22%3A52.936379%2C%22lng%22%3A0.48685761%7D%7D%2C%7B%22dealerNumber%22%3A%22dc5ae562-c133-426a-b8a2-a4b5b94f214c%22%2C%22distance%22%3A139181.54528469374%2C%22location%22%3A%7B%22lat%22%3A51.2928084%2C%22lng%22%3A1.0915843%7D%7D%2C%7B%22dealerNumber%22%3A%22947171ed-b64d-4fb5-ad12-8a39c8f5d297%22%2C%22distance%22%3A140316.073105327%2C%22location%22%3A%7B%22lat%22%3A53.132374%2C%22lng%22%3A-1.1581397%7D%7D%2C%7B%22dealerNumber%22%3A%22946ed83c-fbc5-4d3b-b276-74c840da1557%22%2C%22distance%22%3A142312.02315317094%2C%22location%22%3A%7B%22lat%22%3A50.7752481%2C%22lng%22%3A0.286071%7D%7D%2C%7B%22dealerNumber%22%3A%22a1d240f1-53fb-4b27-b946-f99a7716b88f%22%2C%22distance%22%3A142697.7230800583%2C%22location%22%3A%7B%22lat%22%3A52.015154%2C%22lng%22%3A-2.7333618%7D%7D%2C%7B%22dealerNumber%22%3A%2243fcb79f-f02c-4993-8781-717f4bd0954a%22%2C%22distance%22%3A144734.96543398558%2C%22location%22%3A%7B%22lat%22%3A50.657992%2C%22lng%22%3A-1.2272469%7D%7D%2C%7B%22dealerNumber%22%3A%22fabd2542-533c-4835-937a-494bb945dd95%22%2C%22distance%22%3A146071.8858937064%2C%22location%22%3A%7B%22lat%22%3A53.219405%2C%22lng%22%3A-0.55235601%7D%7D%2C%7B%22dealerNumber%22%3A%2235e47a05-1656-42ac-b417-7979fee9b55c%22%2C%22distance%22%3A147619.24915262716%2C%22location%22%3A%7B%22lat%22%3A50.743483%2C%22lng%22%3A-1.6728543%7D%7D%2C%7B%22dealerNumber%22%3A%228c4ab7ea-bc6f-4865-9cd2-7fcae2e8dcad%22%2C%22distance%22%3A150273.10241951176%2C%22location%22%3A%7B%22lat%22%3A52.376734%2C%22lng%22%3A-2.7235326%7D%7D%2C%7B%22dealerNumber%22%3A%221721378c-8376-4db3-a723-3edf4817afad%22%2C%22distance%22%3A151681.10369375697%2C%22location%22%3A%7B%22lat%22%3A52.713057%2C%22lng%22%3A-2.4593671%7D%7D%2C%7B%22dealerNumber%22%3A%228b2d0e89-b26f-4b69-ac62-79fa39ce45e5%22%2C%22distance%22%3A154576.0791255195%2C%22location%22%3A%7B%22lat%22%3A51.094465%2C%22lng%22%3A1.1467768%7D%7D%2C%7B%22dealerNumber%22%3A%225b0aa761-3dcd-4eaa-8358-9339cd71dd1b%22%2C%22distance%22%3A154998.80920062837%2C%22location%22%3A%7B%22lat%22%3A51.0508391%2C%22lng%22%3A-2.421029%7D%7D%2C%7B%22dealerNumber%22%3A%228f04f746-7161-4eec-b734-008d2c1ea64d%22%2C%22distance%22%3A156439.35167416185%2C%22location%22%3A%7B%22lat%22%3A52.6610653%2C%22lng%22%3A1.2805055%7D%7D%2C%7B%22dealerNumber%22%3A%22c210cf33-1dad-4772-af37-8ef20c21451a%22%2C%22distance%22%3A156478.4288078334%2C%22location%22%3A%7B%22lat%22%3A52.65723%2C%22lng%22%3A1.2850577%7D%7D%2C%7B%22dealerNumber%22%3A%220ce4150a-91c7-487f-8e3a-1f458aa83897%22%2C%22distance%22%3A159390.11301553788%2C%22location%22%3A%7B%22lat%22%3A53.261912%2C%22lng%22%3A-1.4310841%7D%7D%2C%7B%22dealerNumber%22%3A%2263bdda10-24f6-47a3-a3bc-f9a38d0c1b62%22%2C%22distance%22%3A161693.36013561298%2C%22location%22%3A%7B%22lat%22%3A51.619839%2C%22lng%22%3A-2.9602328%7D%7D%2C%7B%22dealerNumber%22%3A%224b56eb25-7fa4-46b4-88a2-21196bb5afea%22%2C%22distance%22%3A162149.8240212788%2C%22location%22%3A%7B%22lat%22%3A53.0291%2C%22lng%22%3A-2.1885609%7D%7D%2C%7B%22dealerNumber%22%3A%2286fa0f73-5df6-424c-bf87-65ccd09f8070%22%2C%22distance%22%3A163137.4511560953%2C%22location%22%3A%7B%22lat%22%3A51.823045%2C%22lng%22%3A-3.0293912%7D%7D%2C%7B%22dealerNumber%22%3A%2259881443-48c8-4cc0-bedd-2f5278a625c1%22%2C%22distance%22%3A169307.13043671745%2C%22location%22%3A%7B%22lat%22%3A52.745303%2C%22lng%22%3A-2.738735%7D%7D%2C%7B%22dealerNumber%22%3A%227a08a60e-1537-408f-94da-90d43b61046c%22%2C%22distance%22%3A170733.5336845417%2C%22location%22%3A%7B%22lat%22%3A51.341217%2C%22lng%22%3A-2.955368%7D%7D%2C%7B%22dealerNumber%22%3A%22efd97fd0-baa5-4d28-ba03-4d0788996711%22%2C%22distance%22%3A175167.7302184923%2C%22location%22%3A%7B%22lat%22%3A53.400104%2C%22lng%22%3A-1.4882151%7D%7D%2C%7B%22dealerNumber%22%3A%22861bd041-0dd9-4c77-aa35-36e6ffdb39b5%22%2C%22distance%22%3A175433.19804053684%2C%22location%22%3A%7B%22lat%22%3A52.470445%2C%22lng%22%3A1.7419595%7D%7D%2C%7B%22dealerNumber%22%3A%22aa71d664-924f-4fec-8096-7c4957e447b7%22%2C%22distance%22%3A178847.3972335906%2C%22location%22%3A%7B%22lat%22%3A53.3245241%2C%22lng%22%3A-1.911525%7D%7D%2C%7B%22dealerNumber%22%3A%22f63ed965-3b6c-43eb-9313-4ca1c9f06149%22%2C%22distance%22%3A181105.48482079%2C%22location%22%3A%7B%22lat%22%3A53.0964515%2C%22lng%22%3A-2.4870292%7D%7D%2C%7B%22dealerNumber%22%3A%22d54d33dc-eeef-4e98-9f49-d7ca27a70828%22%2C%22distance%22%3A182194.22333454792%2C%22location%22%3A%7B%22lat%22%3A51.4665422%2C%22lng%22%3A-3.2020673%7D%7D%2C%7B%22dealerNumber%22%3A%2271f58d7d-4374-4478-ba35-98cdeebedc94%22%2C%22distance%22%3A184588.06455732672%2C%22location%22%3A%7B%22lat%22%3A53.566986%2C%22lng%22%3A-0.63860493%7D%7D%2C%7B%22dealerNumber%22%3A%22971cfb9f-9de8-42d4-a0c5-683d7138a3b0%22%2C%22distance%22%3A184650.4926218104%2C%22location%22%3A%7B%22lat%22%3A53.547063%2C%22lng%22%3A-1.0898524%7D%7D%2C%7B%22dealerNumber%22%3A%22f2f5a915-c3d5-4c48-b797-6f3e6ebdbad9%22%2C%22distance%22%3A188806.07285503668%2C%22location%22%3A%7B%22lat%22%3A53.24737%2C%22lng%22%3A-2.3745388%7D%7D%2C%7B%22dealerNumber%22%3A%225d7c6a33-a214-4ada-97e5-bfe32208fb6d%22%2C%22distance%22%3A189096.25014446583%2C%22location%22%3A%7B%22lat%22%3A53.570304%2C%22lng%22%3A-0.075784539%7D%7D%2C%7B%22dealerNumber%22%3A%229e22cb3f-0771-4d5b-af8d-897b88cd3f24%22%2C%22distance%22%3A189996.33578063425%2C%22location%22%3A%7B%22lat%22%3A52.153643%2C%22lng%22%3A-3.4057891%7D%7D%2C%7B%22dealerNumber%22%3A%22d352aa01-491e-483f-b7a0-e43feef3e4e7%22%2C%22distance%22%3A192141.3590568483%2C%22location%22%3A%7B%22lat%22%3A50.616727%2C%22lng%22%3A-2.4891908%7D%7D%2C%7B%22dealerNumber%22%3A%2203b047fe-a462-4770-bddd-1bf3e554d6ba%22%2C%22distance%22%3A194735.50488822293%2C%22location%22%3A%7B%22lat%22%3A50.7410022%2C%22lng%22%3A-2.744586%7D%7D%2C%7B%22dealerNumber%22%3A%22af14f944-e3e1-493e-b9e5-2877343f0885%22%2C%22distance%22%3A198073.79337733198%2C%22location%22%3A%7B%22lat%22%3A53.640624%2C%22lng%22%3A-1.3357492%7D%7D%2C%7B%22dealerNumber%22%3A%22b8cc7c9e-b47d-4fce-8941-00a50ab30f22%22%2C%22distance%22%3A200302.6584653045%2C%22location%22%3A%7B%22lat%22%3A53.48353%2C%22lng%22%3A-2.0970527%7D%7D%2C%7B%22dealerNumber%22%3A%226a28ef8c-9241-4f0f-ac88-6be5ce6157d1%22%2C%22distance%22%3A200967.59072157668%2C%22location%22%3A%7B%22lat%22%3A50.960869%2C%22lng%22%3A-3.1249141%7D%7D%2C%7B%22dealerNumber%22%3A%22dde58855-23e8-448f-a442-a63c0e8f9df4%22%2C%22distance%22%3A205883.19369037347%2C%22location%22%3A%7B%22lat%22%3A53.747166%2C%22lng%22%3A-0.3241328%7D%7D%2C%7B%22dealerNumber%22%3A%2281f9a68b-f6cd-4875-8088-d1f0f8be88ae%22%2C%22distance%22%3A207024.81978096682%2C%22location%22%3A%7B%22lat%22%3A53.639434%2C%22lng%22%3A-1.7860219%7D%7D%2C%7B%22dealerNumber%22%3A%2297dac648-35f7-44ca-8e04-95c29bf35687%22%2C%22distance%22%3A209936.34348438343%2C%22location%22%3A%7B%22lat%22%3A51.50545%2C%22lng%22%3A-3.6332343%7D%7D%2C%7B%22dealerNumber%22%3A%22dadf0eb8-cee0-43e5-a3fb-95a2c825d80a%22%2C%22distance%22%3A211558.45844822863%2C%22location%22%3A%7B%22lat%22%3A53.398883%2C%22lng%22%3A-2.6051028%7D%7D%2C%7B%22dealerNumber%22%3A%220b267bf9-40f1-4187-8501-8672f1abbdb1%22%2C%22distance%22%3A214986.68802766805%2C%22location%22%3A%7B%22lat%22%3A53.6162322%2C%22lng%22%3A-2.152022%7D%7D%2C%7B%22dealerNumber%22%3A%223b645707-a69c-4aa2-9ddb-5d373e5d08cd%22%2C%22distance%22%3A216325.94660808%2C%22location%22%3A%7B%22lat%22%3A53.780749%2C%22lng%22%3A-1.5244657%7D%7D%2C%7B%22dealerNumber%22%3A%22fe3d65b3-92f6-4986-8a5d-f3e63e34f387%22%2C%22distance%22%3A220307.30797916636%2C%22location%22%3A%7B%22lat%22%3A53.5797694%2C%22lng%22%3A-2.4123791%7D%7D%2C%7B%22dealerNumber%22%3A%22f1e1cebd-1a09-4042-9d73-09080084f927%22%2C%22distance%22%3A220609.50019777185%2C%22location%22%3A%7B%22lat%22%3A53.312664%2C%22lng%22%3A-2.964199%7D%7D%2C%7B%22dealerNumber%22%3A%22b68305fb-1ca0-478b-8fb0-ed7e6ad0cbc0%22%2C%22distance%22%3A221742.9888826722%2C%22location%22%3A%7B%22lat%22%3A53.450228%2C%22lng%22%3A-2.7417443%7D%7D%2C%7B%22dealerNumber%22%3A%22f47c9c08-3c31-4db1-b7d9-ed3930497373%22%2C%22distance%22%3A221810.11716141517%2C%22location%22%3A%7B%22lat%22%3A51.659602%2C%22lng%22%3A-3.8560219%7D%7D%2C%7B%22dealerNumber%22%3A%22fdb49dc2-f977-4b2c-9a75-fbf6e8c721ea%22%2C%22distance%22%3A224466.79240366907%2C%22location%22%3A%7B%22lat%22%3A53.8121591%2C%22lng%22%3A-1.7633073%7D%7D%2C%7B%22dealerNumber%22%3A%22bc32afd4-66f0-4707-bfa4-14401ebbb032%22%2C%22distance%22%3A225797.62870798097%2C%22location%22%3A%7B%22lat%22%3A53.5421955%2C%22lng%22%3A-2.6464499%7D%7D%2C%7B%22dealerNumber%22%3A%226505ea1f-d08c-42af-8945-953bb008633e%22%2C%22distance%22%3A232545.53027875532%2C%22location%22%3A%7B%22lat%22%3A53.855901%2C%22lng%22%3A-1.9147824%7D%7D%2C%7B%22dealerNumber%22%3A%2264e28a85-174f-4c37-a71d-4ba3ff0e659c%22%2C%22distance%22%3A232695.56681910358%2C%22location%22%3A%7B%22lat%22%3A53.979585%2C%22lng%22%3A-1.1343047%7D%7D%2C%7B%22dealerNumber%22%3A%220b48a6a8-3866-46d6-9f2a-92b523acd72c%22%2C%22distance%22%3A235315.70500029114%2C%22location%22%3A%7B%22lat%22%3A51.793387%2C%22lng%22%3A-4.0774524%7D%7D%2C%7B%22dealerNumber%22%3A%22acbf5287-5842-48f8-b21a-a64a7fb119a3%22%2C%22distance%22%3A237280.3147651055%2C%22location%22%3A%7B%22lat%22%3A53.7471452%2C%22lng%22%3A-2.4463172%7D%7D%2C%7B%22dealerNumber%22%3A%22de95bbe9-52b2-4f2a-a947-2f8881b62a10%22%2C%22distance%22%3A238299.5432231086%2C%22location%22%3A%7B%22lat%22%3A52.743293%2C%22lng%22%3A-3.8861024%7D%7D%2C%7B%22dealerNumber%22%3A%227cd3515b-6de7-4279-aa27-6cc773687bac%22%2C%22distance%22%3A240225.38213050715%2C%22location%22%3A%7B%22lat%22%3A50.703627%2C%22lng%22%3A-3.5239627%7D%7D%2C%7B%22dealerNumber%22%3A%22838b1c4f-4b63-41f1-9c68-b3c2ff9673ad%22%2C%22distance%22%3A247338.96122654463%2C%22location%22%3A%7B%22lat%22%3A53.60422%2C%22lng%22%3A-3.0337439%7D%7D%2C%7B%22dealerNumber%22%3A%22896f5953-0746-4192-a70e-e801a2cb4dc0%22%2C%22distance%22%3A249307.07112625815%2C%22location%22%3A%7B%22lat%22%3A53.773968%2C%22lng%22%3A-2.7132411%7D%7D%2C%7B%22dealerNumber%22%3A%226fe74dda-2181-427d-8f4a-3c4a62ca7cb6%22%2C%22distance%22%3A249751.22918413192%2C%22location%22%3A%7B%22lat%22%3A53.286176%2C%22lng%22%3A-3.576431%7D%7D%2C%7B%22dealerNumber%22%3A%2223b92ba8-16e9-4305-a4f3-048877420f06%22%2C%22distance%22%3A252861.8076617492%2C%22location%22%3A%7B%22lat%22%3A51.075647%2C%22lng%22%3A-4.0545688%7D%7D%2C%7B%22dealerNumber%22%3A%227d40dff1-a5c4-4a32-b27f-5485372a4bb5%22%2C%22distance%22%3A253686.08431514655%2C%22location%22%3A%7B%22lat%22%3A54.129243%2C%22lng%22%3A-1.5134008%7D%7D%2C%7B%22dealerNumber%22%3A%224a8feff0-308d-47c3-a297-62c72d20e0a8%22%2C%22distance%22%3A261411.80544016833%2C%22location%22%3A%7B%22lat%22%3A52.927936%2C%22lng%22%3A-4.1296278%7D%7D%2C%7B%22dealerNumber%22%3A%22306e6c3d-256c-45f1-bfb7-730898923058%22%2C%22distance%22%3A264944.5264621089%2C%22location%22%3A%7B%22lat%22%3A54.284208%2C%22lng%22%3A-0.41146216%7D%7D%2C%7B%22dealerNumber%22%3A%220223cc5f-a0d0-49b5-a03f-6522396f9b88%22%2C%22distance%22%3A279917.2256618723%2C%22location%22%3A%7B%22lat%22%3A53.233163%2C%22lng%22%3A-4.177928%7D%7D%2C%7B%22dealerNumber%22%3A%2264095860-6900-4ce4-b466-913902d05d5a%22%2C%22distance%22%3A283262.40742187353%2C%22location%22%3A%7B%22lat%22%3A50.285498%2C%22lng%22%3A-3.7811485%7D%7D%2C%7B%22dealerNumber%22%3A%22ea9b996f-04a4-43d7-9224-b9e1d160be1c%22%2C%22distance%22%3A292081.0750845552%2C%22location%22%3A%7B%22lat%22%3A50.388598%2C%22lng%22%3A-4.0700311%7D%7D%2C%7B%22dealerNumber%22%3A%22bd9fca76-51ca-4985-91b4-5f2e441ddc75%22%2C%22distance%22%3A297494.8897735902%2C%22location%22%3A%7B%22lat%22%3A54.530861%2C%22lng%22%3A-1.5236435%7D%7D%2C%7B%22dealerNumber%22%3A%227d634e86-8dcf-469b-86e6-0f7b9e375aef%22%2C%22distance%22%3A298467.12775335746%2C%22location%22%3A%7B%22lat%22%3A54.568728%2C%22lng%22%3A-1.2240381%7D%7D%2C%7B%22dealerNumber%22%3A%2249d4a5e8-44b2-4f9b-a6cb-7efa60302fb0%22%2C%22distance%22%3A298661.4944809939%2C%22location%22%3A%7B%22lat%22%3A51.75746%2C%22lng%22%3A-4.9954625%7D%7D%2C%7B%22dealerNumber%22%3A%22874e236d-6c9f-4bd7-8cd0-e28b28f76f95%22%2C%22distance%22%3A304019.5226393571%2C%22location%22%3A%7B%22lat%22%3A54.337751%2C%22lng%22%3A-2.7419168%7D%7D%2C%7B%22dealerNumber%22%3A%22ea9adb66-1baf-470c-9e9c-d31bfa6e61ea%22%2C%22distance%22%3A307152.20747590647%2C%22location%22%3A%7B%22lat%22%3A49.4301647%2C%22lng%22%3A-2.5734796%7D%7D%2C%7B%22dealerNumber%22%3A%22bb39b0f0-0cca-48ca-90f0-0bf1f18efea3%22%2C%22distance%22%3A314080.3345539065%2C%22location%22%3A%7B%22lat%22%3A50.457779%2C%22lng%22%3A-4.5213176%7D%7D%2C%7B%22dealerNumber%22%3A%22c1e88743-2816-4724-ac16-1fa301672b65%22%2C%22distance%22%3A317374.4122981947%2C%22location%22%3A%7B%22lat%22%3A49.2187%2C%22lng%22%3A-2.1472%7D%7D%2C%7B%22dealerNumber%22%3A%228db5fa04-57b4-4896-9a5c-2f3ca71b248b%22%2C%22distance%22%3A322765.7272737975%2C%22location%22%3A%7B%22lat%22%3A54.749838%2C%22lng%22%3A-1.6308389%7D%7D%2C%7B%22dealerNumber%22%3A%22bd430529-4175-45eb-8500-7f2d072ef2b9%22%2C%22distance%22%3A344675.9212172895%2C%22location%22%3A%7B%22lat%22%3A54.9539587%2C%22lng%22%3A-1.601768%7D%7D%2C%7B%22dealerNumber%22%3A%22ca2fd0a4-91bf-4049-a923-d6c4859d8468%22%2C%22distance%22%3A347015.6463464733%2C%22location%22%3A%7B%22lat%22%3A50.365666%2C%22lng%22%3A-4.9781307%7D%7D%2C%7B%22dealerNumber%22%3A%22969cd3db-2339-4752-8601-fd32039512c4%22%2C%22distance%22%3A349917.4811766109%2C%22location%22%3A%7B%22lat%22%3A55.012655%2C%22lng%22%3A-1.4957791%7D%7D%2C%7B%22dealerNumber%22%3A%22ca25a656-ba86-4a61-ad95-3ca42cb58c12%22%2C%22distance%22%3A354470.61681386613%2C%22location%22%3A%7B%22lat%22%3A54.97524%2C%22lng%22%3A-2.1023601%7D%7D%2C%7B%22dealerNumber%22%3A%225ee4d416-b407-4e91-8efa-7fb437cefb83%22%2C%22distance%22%3A359614.7118774103%2C%22location%22%3A%7B%22lat%22%3A54.15015%2C%22lng%22%3A-4.530566%7D%7D%2C%7B%22dealerNumber%22%3A%223f048056-090d-488a-9bda-1a2b5db34c0d%22%2C%22distance%22%3A361401.00808584533%2C%22location%22%3A%7B%22lat%22%3A54.656897%2C%22lng%22%3A-3.5534179%7D%7D%2C%7B%22dealerNumber%22%3A%221d9ca580-df7b-4da3-a3cf-3482a1abd082%22%2C%22distance%22%3A364213.76256600535%2C%22location%22%3A%7B%22lat%22%3A54.8961323%2C%22lng%22%3A-2.900139%7D%7D%2C%7B%22dealerNumber%22%3A%2288686154-20b1-4d87-803a-5210a3533db9%22%2C%22distance%22%3A366576.30594311573%2C%22location%22%3A%7B%22lat%22%3A50.257627%2C%22lng%22%3A-5.1971131%7D%7D%2C%7B%22dealerNumber%22%3A%22b009de40-9fad-4eef-a51f-2cb3dfe1d46b%22%2C%22distance%22%3A368180.67399529746%2C%22location%22%3A%7B%22lat%22%3A55.1615777%2C%22lng%22%3A-1.6689117%7D%7D%2C%7B%22dealerNumber%22%3A%22809e2582-0a2a-4cc5-a9f6-54c082f27a0d%22%2C%22distance%22%3A394355.455836248%2C%22location%22%3A%7B%22lat%22%3A55.398635%2C%22lng%22%3A-1.6890674%7D%7D%2C%7B%22dealerNumber%22%3A%22512b675e-18dd-42d7-a84a-bdeaa3f428a7%22%2C%22distance%22%3A403106.74364741606%2C%22location%22%3A%7B%22lat%22%3A55.0705737%2C%22lng%22%3A-3.6298751%7D%7D%2C%7B%22dealerNumber%22%3A%22c9ae3419-207a-465b-a117-ee6651e2d22d%22%2C%22distance%22%3A451709.1296817861%2C%22location%22%3A%7B%22lat%22%3A54.6452%2C%22lng%22%3A-5.6752%7D%7D%2C%7B%22dealerNumber%22%3A%225e216cbf-eeb7-4672-bd0a-c8c4e0fff5fb%22%2C%22distance%22%3A469484.966054407%2C%22location%22%3A%7B%22lat%22%3A54.6729%2C%22lng%22%3A-5.99367%7D%7D%2C%7B%22dealerNumber%22%3A%224e91c131-fbfd-423e-b9a1-b1ac4cde9444%22%2C%22distance%22%3A471105.73917473055%2C%22location%22%3A%7B%22lat%22%3A54.4606%2C%22lng%22%3A-6.29865%7D%7D%2C%7B%22dealerNumber%22%3A%22832b043c-df80-4a3e-8d64-14bd9f6432eb%22%2C%22distance%22%3A474491.3255879552%2C%22location%22%3A%7B%22lat%22%3A55.941265%2C%22lng%22%3A-3.0092124%7D%7D%2C%7B%22dealerNumber%22%3A%226bf9d5b5-4488-4200-a146-5fc54104ed18%22%2C%22distance%22%3A479641.2877849006%2C%22location%22%3A%7B%22lat%22%3A55.9279828%2C%22lng%22%3A-3.3006115%7D%7D%2C%7B%22dealerNumber%22%3A%224c939020-dc41-4ace-af82-e136a20fe281%22%2C%22distance%22%3A487687.5194418012%2C%22location%22%3A%7B%22lat%22%3A55.607746%2C%22lng%22%3A-4.6360918%7D%7D%2C%7B%22dealerNumber%22%3A%226229ecb1-4603-47d9-ba85-0b210baf0a4f%22%2C%22distance%22%3A487998.04544799525%2C%22location%22%3A%7B%22lat%22%3A55.776858%2C%22lng%22%3A-4.1614431%7D%7D%2C%7B%22dealerNumber%22%3A%22f933c23d-2fd6-4392-aa93-b793b78919f2%22%2C%22distance%22%3A490579.7255486057%2C%22location%22%3A%7B%22lat%22%3A55.846153%2C%22lng%22%3A-4.0228806%7D%7D%2C%7B%22dealerNumber%22%3A%2224870366-c93f-4538-9f6d-ae94748a9768%22%2C%22distance%22%3A497270.1650232153%2C%22location%22%3A%7B%22lat%22%3A55.8341641%2C%22lng%22%3A-4.2816592%7D%7D%2C%7B%22dealerNumber%22%3A%22e1f65e9d-9632-40b2-952a-0e16bd8a9c47%22%2C%22distance%22%3A497575.65755748696%2C%22location%22%3A%7B%22lat%22%3A56.13625%2C%22lng%22%3A-3.1355786%7D%7D%2C%7B%22dealerNumber%22%3A%228ed4f6fe-5b25-43ed-b9c1-c4150c678849%22%2C%22distance%22%3A501064.2069647522%2C%22location%22%3A%7B%22lat%22%3A56.00669%2C%22lng%22%3A-3.8299193%7D%7D%2C%7B%22dealerNumber%22%3A%22ee63252b-3f70-4768-ae90-66d6965bf3ad%22%2C%22distance%22%3A512894.5234712665%2C%22location%22%3A%7B%22lat%22%3A55.793461%2C%22lng%22%3A-4.8660536%7D%7D%2C%7B%22dealerNumber%22%3A%22d559d222-255d-4474-b4c7-f4a3106f11fa%22%2C%22distance%22%3A521292.844052071%2C%22location%22%3A%7B%22lat%22%3A55.876061%2C%22lng%22%3A-4.8883701%7D%7D%2C%7B%22dealerNumber%22%3A%22ade10028-f790-41bf-98e4-d6c2b00df7db%22%2C%22distance%22%3A527379.0951246194%2C%22location%22%3A%7B%22lat%22%3A56.468269%2C%22lng%22%3A-2.8633743%7D%7D%2C%7B%22dealerNumber%22%3A%22a6ba8b16-b642-475c-8e8c-3da8f8a56e8f%22%2C%22distance%22%3A538714.5556118429%2C%22location%22%3A%7B%22lat%22%3A56.375555%2C%22lng%22%3A-3.8449285%7D%7D%2C%7B%22dealerNumber%22%3A%220d4f4dac-56a8-4ec7-811b-896d14de6356%22%2C%22distance%22%3A551456.511516929%2C%22location%22%3A%7B%22lat%22%3A54.7565144%2C%22lng%22%3A-7.4550939%7D%7D%2C%7B%22dealerNumber%22%3A%22e8bbfa5c-1ffb-4a54-85a9-a58633330472%22%2C%22distance%22%3A600521.9688255345%2C%22location%22%3A%7B%22lat%22%3A57.215096%2C%22lng%22%3A-2.3411501%7D%7D%2C%7B%22dealerNumber%22%3A%2223c772e6-91be-4153-8fe0-e88875120eae%22%2C%22distance%22%3A628233.9824665921%2C%22location%22%3A%7B%22lat%22%3A57.513391%2C%22lng%22%3A-1.8096018%7D%7D%2C%7B%22dealerNumber%22%3A%229a918f2d-3042-4f23-a213-58767c832d24%22%2C%22distance%22%3A662267.963974762%2C%22location%22%3A%7B%22lat%22%3A57.487105%2C%22lng%22%3A-4.2490284%7D%7D%2C%7B%22dealerNumber%22%3A%22e64b5c0f-80e8-4b42-bc36-c5a7c8307c74%22%2C%22distance%22%3A920085.699849764%2C%22location%22%3A%7B%22lat%22%3A60.169353%2C%22lng%22%3A-1.1661518%7D%7D%2C%7B%22dealerNumber%22%3A%22f939bd70-1012-4ed7-b1d0-61740c58101c%22%2C%22distance%22%3A15412164.216824647%2C%22location%22%3A%7B%22lat%22%3A-17.6297185%2C%22lng%22%3A149.5041682%7D%7D%5D&PostcodeForDealers="

        payload = start_payload + pay_data + mid_payload + str(lat) + ", " + str(lng)

        try:
            store_data = session.post(api_link, headers=headers, data=payload).json()
        except:
            continue

        stores = store_data["dealers"]
        stores.insert(0, store_data["recommmendedDealer"])

        for store in stores:
            final_link = "https://cars.suzuki.co.uk" + store["dealerLink"]["url"]

            location_name = store["name"]
            raw_address = store["address"].split("<br/>")
            street_address = raw_address[0]
            city = raw_address[1]
            try:
                state = raw_address[2]
                if not state:
                    state = "<MISSING>"
            except:
                state = "<MISSING>"
            zip_code = store["postcode"]
            country_code = "UK"
            store_number = store["dealerNumber"]
            if store_number in dup_tracker:
                continue
            dup_tracker.append(store_number)
            location_type = "<MISSING>"
            phone = store["contacts"][0]["phoneNumber"]

            try:
                hours_of_operation = ""
                raw_hours = store["hours"][0]["details"]

                for row in raw_hours:
                    hours_of_operation = (
                        hours_of_operation + " " + row["day"] + " " + row["times"]
                    ).strip()
            except:
                hours_of_operation = "<MISSING>"

            log.info(final_link)
            req = session.get(final_link, headers=get_headers)
            base = BeautifulSoup(req.text, "lxml")

            latitude = base.find(class_="google-map")["data-pin-lat"]
            longitude = base.find(class_="google-map")["data-pin-lng"]

            yield [
                locator_domain,
                final_link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
