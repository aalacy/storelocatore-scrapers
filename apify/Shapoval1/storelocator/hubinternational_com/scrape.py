import csv
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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
    out = []

    locator_domain = "https://www.hubinternational.com/"

    api_url = "https://www.hubinternational.com/coveo/rest/v2?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7B5AFB340B-0CED-4466-B346-2F74EBE8FB11%7D%3Flang%3Den%26amp%3Bver%3D1&siteName=hub"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    states = [
        "WY",
        "WV",
        "WI",
        "WA",
        "VT",
        "VA",
        "UT",
        "TX",
        "TN",
        "SD",
        "SC",
        "RI",
        "PR",
        "PA",
        "OR",
        "OK",
        "OH",
        "NY",
        "NV",
        "NM",
        "NJ",
        "NH",
        "NE",
        "ND",
        "NC",
        "MT",
        "MS",
        "MO",
        "MN",
        "MI",
        "ME",
        "MD",
        "MA",
        "LA",
        "KY",
        "KS",
        "IN",
        "IL",
        "ID",
        "IA",
        "HI",
        "GA",
        "FL",
        "DE",
        "DC",
        "CT",
        "CO",
        "CA",
        "AZ",
        "AR",
        "AL",
        "AK",
        "BC",
        "ON",
        "AB",
        "MB",
        "NB",
        "NL",
        "NT",
        "NS",
        "NU",
        "PE",
        "QC",
        "SK",
        "YT",
    ]

    for state in states:
        data = {
            "$actionsHistory": '[{"name":"Query","time":"\\"2021-06-17T20:03:41.628Z\\""},{"name":"Query","time":"\\"2021-06-17T19:54:09.170Z\\""},{"name":"Query","time":"\\"2021-06-17T05:55:38.107Z\\""},{"name":"Query","time":"\\"2021-06-16T21:14:30.001Z\\""},{"name":"Query","time":"\\"2021-06-16T21:10:02.324Z\\""},{"name":"Query","time":"\\"2021-06-16T20:57:33.174Z\\""},{"name":"Query","time":"\\"2021-06-16T16:57:54.493Z\\""},{"name":"Query","time":"\\"2021-06-16T16:55:23.880Z\\""}]',
            "referrer": "",
            "visitorId": "80a170d4-c0ca-439e-a6df-663215fb16df",
            "isGuestUser": "false",
            "aq": f"($qf(function:'dist(@flatitude14371, @flongitude14371,41.8780439,-87.6257476) * 0.000621371192 ', fieldName: 'distance')  @distance <1000) (@statesz32xtitle={state} OR @provincesz32xtitle={state}) (((@z95xpath==EF7F6A4664EB485690DEC2F6D2725F3D (@haslayout==1 @z95xtemplate==5A0F7485CE5E42EE902D79B964A014B8)) NOT @z95xtemplate==(ADB6CA4F03EF4F47B9AC9CE2BA53FF97,FE5DD82648C6436DB87A7C4210C7413B))) (@source==\"Coveo_pub_index - ncu-prd-82ff54d70ef8-xp3\")",
            "cq": "(@z95xlanguage==en) (@z95xlatestversion==1)",
            "searchHub": "offices",
            "locale": "en",
            "maximumAge": "900000",
            "firstResult": "0",
            "numberOfResults": "100",
            "excerptLength": "200",
            "enableDidYouMean": "false",
            "sortCriteria": "@distance ascending",
            "queryFunctions": "[]",
            "rankingFunctions": "[]",
            "groupBy": '[{"field":"@linesz32xofz32xbusinessz32xtitle","queryOverride":"($qf(function:\'dist(@flatitude14371, @flongitude14371,41.8780439,-87.6257476) * 0.000621371192 \', fieldName: \'distance\')  @distance <1000) (@statesz32xtitle=IL OR @provincesz32xtitle=IL) (((@z95xpath==EF7F6A4664EB485690DEC2F6D2725F3D (@haslayout==1 @z95xtemplate==5A0F7485CE5E42EE902D79B964A014B8)) NOT @z95xtemplate==(ADB6CA4F03EF4F47B9AC9CE2BA53FF97,FE5DD82648C6436DB87A7C4210C7413B))) (@source==\\"Coveo_pub_index - ncu-prd-82ff54d70ef8-xp3\\")","constantQueryOverride":"(@z95xlanguage==en) (@z95xlatestversion==1)"}]',
            "facetOptions": "{}",
            "categoryFacets": "[]",
            "retrieveFirstSentences": "true",
            "timezone": "Europe/Moscow",
            "enableQuerySyntax": "false",
            "enableDuplicateFiltering": "false",
            "enableCollaborativeRating": "false",
            "debug": "false",
            "allowQueriesWithoutKeywords": "true",
        }
        r = session.post(api_url, headers=headers, data=data)
        js = r.json()["results"]
        for j in js:

            page_url = j.get("clickUri")
            location_name = "".join(j.get("title"))
            if location_name.find("(") != -1:
                location_name = location_name.split("(")[0].strip()
            if location_name.find(",") != -1:
                location_name = location_name.split(",")[0].strip()
            location_type = "<MISSING>"
            street_address = j.get("raw").get("faddress14371")
            latitude = j.get("raw").get("flatitude14371")
            longitude = j.get("raw").get("flongitude14371")

            country_code = "<MISSING>"
            if "/us/" in page_url:
                country_code = "US"
            if "/ca/" in page_url:
                country_code = "CA"
            state = state
            postal = j.get("raw").get("fz122xip14371")
            city = j.get("raw").get("fcity14371")
            if "10016" in city:
                city = "New York"
            store_number = "<MISSING>"
            phone = j.get("raw").get("fphone14371") or "<MISSING>"
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = tree.xpath('//div[@class="hours-content"]//text()')
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
            hours_of_operation = hours_of_operation.replace("Office Hours", "").strip()
            if hours_of_operation.find("CLOSURE") != -1:
                hours_of_operation = "Closed"
            if hours_of_operation.find("COVID-19") != -1:
                hours_of_operation = "<MISSING>"
            hours_of_operation = (
                hours_of_operation.replace("Heures de travail", "")
                .replace("Lundi", "Monday")
                .replace("Mardi", "Tuesday")
                .replace("Mercredi", "Wednesday")
                .replace("Jeudi", "Thursday")
                .replace("Vendredi", "Friday")
                .replace("Samedi", "Saturday")
                .replace("Dimanche", "Sunday")
                .replace("Ferme", "Closed")
                .strip()
            )

            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                postal,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
