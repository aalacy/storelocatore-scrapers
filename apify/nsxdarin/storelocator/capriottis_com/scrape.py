import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJRQ2hpc1p1SUExdzk0MVBJTlRKTk1QSXo3bG55RlFWTmNFU2tIRVR0azlieVBEeHowNlNyeVlYZXBDalh0bVZkcmZHdm0zNGUyMG9GM0hYejBVdHBiM0dReWpBeHA1N0NYTVE5WGJoZ09aWmg2djVsQ1hIblE2SkYiLCJqdGkiOiI5MmNiNjg1YzQxMDZkNDMwN2QwM2VmMzI0Nzc2NzI1Y2NiZDMxNDhkNGU0NGYyZDY2MDg2Y2JmMGM2ZmVhNDE2Y2ZmOWRlMWQ1Y2FkY2Y1MSIsImlhdCI6MTYyMzE2MTQ1MiwibmJmIjoxNjIzMTYxNDUyLCJleHAiOjE2MjMyNDc4NTIsInN1YiI6IiIsInNjb3BlcyI6WyJhbGxlcmdpZXM6aW5kZXgiLCJhbmFseXRpY3NfZXZlbnRzOnNob3dfc2NoZW1hIiwiYmFza2V0X2xveWFsdHk6YXBwbHlfcmV3YXJkcyIsImJhc2tldF9sb3lhbHR5OmRlc3Ryb3lfcmV3YXJkIiwiYmFza2V0X2xveWFsdHk6Z2V0X2FwcGxpZWRfcmV3YXJkcyIsImJhc2tldF9sb3lhbHR5OmdldF9hdmFpbGFibGVfcmV3YXJkcyIsImJhc2tldHM6ZGVzdHJveV9wcm9tb19jb2RlIiwiYmFza2V0czpkZXN0cm95X3dhbnRlZF90aW1lIiwiYmFza2V0czpnZXRfYXZhaWxhYmxlX3dhbnRlZF90aW1lcyIsImJhc2tldHM6bGlzdF9yZXF1aXJlZF92ZXJpZmljYXRpb25zIiwiYmFza2V0czpzZXRfY29udmV5YW5jZSIsImJhc2tldHM6c2hvdyIsImJhc2tldHM6c3RvcmUiLCJiYXNrZXRzOnN0b3JlX2FsbGVyZ2llcyIsImJhc2tldHM6c3RvcmVfcHJvbW9fY29kZSIsImJhc2tldHM6c3RvcmVfd2FudGVkX3RpbWUiLCJiYXNrZXRzOnN1Ym1pdCIsImJhc2tldHM6dmFsaWRhdGVfYmFza2V0IiwiYmFza2V0czp2ZXJpZnlfYmFza2V0IiwiY29uZmlnOnNob3ciLCJncm91cDpvcmRlcmluZ19hcHAiLCJsb2NhdGlvbl9tZW51OnNob3ciLCJsb3lhbHR5OmNoZWNrX3JlZ2lzdHJhdGlvbl9zdGF0dXMiLCJsb3lhbHR5OmNyZWF0ZV9yZWRlbXB0aW9uIiwibG95YWx0eTpmb3Jnb3RfcGFzc3dvcmQiLCJsb3lhbHR5OmluZGV4X3JlZGVlbWFibGVzIiwibG95YWx0eTppbmRleF9yZWRlbXB0aW9ucyIsImxveWFsdHk6cmVnaXN0ZXIiLCJsb3lhbHR5OnJlc2V0X3Bhc3N3b3JkIiwibG95YWx0eTpzaG93X2xveWFsdHlfc3RhdGUiLCJsb3lhbHR5OnNob3dfbWUiLCJsb3lhbHR5OnVwZGF0ZV9tZSIsIm9yZGVyX2xveWFsdHk6Y2xhaW1fcmV3YXJkcyIsIm9yZGVyczpkZXN0cm95X2Zhdm9yaXRlIiwib3JkZXJzOmRpc3BhdGNoX3JlY2VpcHRfZW1haWwiLCJvcmRlcnM6aW5kZXhfZmF2b3JpdGVzIiwib3JkZXJzOmluZGV4X215X29yZGVycyIsIm9yZGVyczpzdG9yZV9mYXZvcml0ZSIsInN0b3JlX2xvY2F0aW9uczpkZXN0cm95X2Zhdm9yaXRlIiwic3RvcmVfbG9jYXRpb25zOmluZGV4Iiwic3RvcmVfbG9jYXRpb25zOmluZGV4X2Zhdm9yaXRlcyIsInN0b3JlX2xvY2F0aW9uczpzaG93Iiwic3RvcmVfbG9jYXRpb25zOnN0b3JlX2Zhdm9yaXRlIiwidGFnczppbmRleCIsInVwc2VsbHM6Z2VuZXJhdGUiLCJ1c2VyczpkZXN0cm95X3N0b3JlZF9jYXJkIiwidXNlcnM6aW5kZXhfc3RvcmVkX2NhcmRzIl19.raoe0VUSZuVcGfMd89QhWu0hc0Db5xWQUbTUDdjA5stVGrn_TfpLlKcmPH7CapnLF_QvfBggW-ItCbHiuHtA__Z6pI_90zPESFZM7ZN8OQeZZ1eYVAjeptmz6GwkPYNmn1le0c4R1CvUHtDZkiGA-L38FmaaWmW2X3pDHRGhQqAa6cxkfRNbhgqW4DhaXC25WiqYR_RwoI7UOII-tTobGZAZPANChKGlckw9-LoMkg_GL7MuAHelsvpgwFEQ3byBIFR2FSvd44HU1aRM70JlAdS0z8TzGnNh_3isJ5Fx2MMe_mqDMITKQXMnWT_76H0p6BUYkx8H2w3mZ8rZxJmtiTVBbav6eIDhum_TITuxec1J4RNQTQfwyNkpDi9iuyup0QfaiJXzS165cBKJ068_9-wjCU8UBb6f6IJ-GZnJ93ua5JSkOz2dK2qYc9L61ZJGaB4C2Vn2EdUbhHZXRF2vLOyyfqIa2iycKOqXsaQB46C5910HcXoVJePoobbWGboOCBepVbJ1joA-EqofF2mtPaDteOtsELen9X9bARjJPGrdRJBHMP03NSpcpAVvO6RDZssA3_5EfAMNWOq5JPM0cF1FlSGjJuYMeVImNGINcu12Kyn2LOWWmnVqnxrYBs15o4muRfojveCH_QGANGwbgtquAX96Ec4cVX_IAZQiGI0",
}

logger = SgLogSetup().get_logger("capriottis_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    for x in range(1, 6):
        url = (
            "https://api.koala.io/v1/ordering/store-locations/?sort[state_id]=asc&sort[label]=asc&include[]=operating_hours&include[]=attributes&include[]=delivery_hours&page="
            + str(x)
            + "&per_page=50"
        )
        r = session.get(url, headers=headers)
        website = "capriottis.com"
        typ = "<MISSING>"
        country = "US"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"location_id":"' in line:
                items = line.split('"location_id":"')
                for item in items:
                    if '"latitude":' in item:
                        store = item.split('"')[0]
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        zc = item.split('"zip":"')[1].split('"')[0]
                        name = item.split('"label":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        phone = item.split('"phone_number":"')[1].split('"')[0]
                        add = item.split('"street_address":"')[1].split('"')[0]
                        lurl = (
                            "https://capriottis.olo.com/menu/"
                            + item.split('"slug":"')[1].split('"')[0]
                        )
                        hours = "<INACCESSIBLE>"
                        name = name.replace("\\u2019", "'")
                        yield [
                            website,
                            lurl,
                            name,
                            add,
                            city,
                            state,
                            zc,
                            country,
                            store,
                            phone,
                            typ,
                            lat,
                            lng,
                            hours,
                        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
