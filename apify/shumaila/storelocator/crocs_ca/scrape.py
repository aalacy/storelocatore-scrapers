import csv
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    p = 0
    data = []
    key_set = set([])
    zips = static_zipcode_list(radius=100, country_code=SearchableCountries.CANADA)
    for zip_code in zips:
        datam = (
            '{"request":{"appkey":"1BC4F6AA-9BB9-11E6-953B-FA25F3F215A2","formdata":{"geoip":false,"dataview":"store_default","order":"icon DESC,_distance","limit":100000,"geolocs":{"geoloc":[{"addressline":"'
            + str(zip_code)
            + '","country":"CA","latitude":"","longitude":""}]},"searchradius":"'
            + "250"
            + '","radiusuom":"km","where":{"TBLSTORESTATUS":{"in":"Open,OPEN,open"},"or":{"crocsretail":{"eq":"1"},"crocsoutlet":{"eq":"1"},"otherretailer":{"eq":"1"}}},"false":"0"}}}'
        )
        res = session.post("https://stores.crocs.com/rest/locatorsearch", data=datam)
        try:
            jso = res.json()["response"]["collection"]
        except:
            continue
        for js in jso:
            if js["country"] != "CA":
                continue
            try:
                loc = js["name"]
            except:
                continue
            try:
                sid = js["uid"]
            except:
                sid = "<MISSING>"
            try:
                hours = (
                    "Monday "
                    + js["monopen"]
                    + "-"
                    + js["monclose"]
                    + " Tuesday "
                    + js["tueopen"]
                    + "-"
                    + js["tueclose"]
                    + " Wednesday "
                    + js["wedopen"]
                    + "-"
                    + js["wedclose"]
                    + " Thursday "
                    + js["thropen"]
                    + "-"
                    + js["thrclose"]
                    + " Friday "
                    + js["friopen"]
                    + "-"
                    + js["friclose"]
                    + " Saturday "
                    + js["satopen"]
                    + "-"
                    + js["satclose"]
                    + " Sunday "
                    + js["sunopen"]
                    + "-"
                    + js["sunclose"]
                    + " "
                )
            except:
                hours = "<MISSING>"
            lat = js["latitude"]
            long = js["longitude"]
            street = js["address1"]
            state = js["province"]
            szip = js["postalcode"]
            if szip is None:
                szip = "<MISSING>"
            city = js["city"]
            key = loc + city + szip + state
            if key in key_set:
                continue
            key_set.add(key)

            try:
                phone = js["phone"]
            except:
                phone = None
            if phone == "null" or phone == "" or phone is None:
                phone = "<MISSING>"
            ltype = js["tblstoretype"]

            data.append(
                [
                    "https://www.crocs.ca/",
                    loc,
                    street,
                    city,
                    state,
                    szip,
                    "CA",
                    sid,
                    phone,
                    ltype,
                    lat,
                    long,
                    hours,
                    "https://www.crocs.ca/store-locator/stores,en_CA,pg.html",
                ]
            )

            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
