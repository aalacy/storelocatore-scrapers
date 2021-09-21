from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dairyqueen_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.CANADA],
    max_search_distance_miles=None,
    max_search_results=50,
)

allcities = [
    "43.719|-79.401",
    "45.576|-73.587",
    "51.045|-114.037",
    "45.195|-75.799",
    "53.518|-113.53",
    "43.616|-79.655",
    "49.87|-97.132",
    "49.247|-123.064",
    "43.715|-79.745",
    "43.291|-80.046",
    "46.868|-71.276",
    "49.12|-122.772",
    "45.609|-73.72",
    "44.945|-63.088",
    "42.953|-81.23",
    "43.889|-79.285",
    "43.836|-79.566",
    "45.511|-75.64",
    "52.146|-106.62",
    "45.524|-73.455",
    "43.418|-80.468",
    "49.244|-122.977",
    "42.283|-82.994",
    "50.449|-104.634",
    "49.154|-123.125",
    "43.903|-79.428",
    "43.452|-79.73",
    "43.379|-79.825",
    "46.581|-80.974",
    "45.376|-72.002",
    "43.95|-78.879",
    "48.359|-71.161",
    "46.708|-71.203",
    "44.362|-79.689",
    "49.067|-122.277",
    "49.317|-122.743",
    "46.372|-72.61",
    "43.161|-79.255",
    "43.546|-80.234",
    "43.422|-80.329",
    "43.935|-78.966",
    "49.886|-119.44",
    "44.281|-76.559",
    "43.872|-79.027",
    "49.086|-122.549",
    "48.505|-123.406",
    "45.717|-73.717",
    "43.523|-80.022",
    "47.431|-52.793",
    "48.433|-89.312",
    "43.469|-80.565",
    "49.121|-122.956",
    "42.429|-82.165",
    "52.282|-113.801",
    "53.533|-113.122",
    "43.155|-80.266",
    "45.324|-73.317",
    "46.254|-60.024",
    "49.697|-112.824",
    "43.978|-78.668",
    "43.93|-79.139",
    "49.213|-123.995",
    "50.68|-120.411",
    "43.025|-79.111",
    "49.36|-122.997",
    "48.428|-123.35",
    "45.451|-73.457",
    "45.769|-73.494",
    "44.05|-79.461",
    "49.146|-121.877",
    "49.267|-122.512",
    "44.298|-78.329",
    "44.49|-78.794",
    "45.888|-72.512",
    "45.787|-74.009",
    "53.911|-122.793",
    "46.56|-84.322",
    "46.116|-64.812",
    "42.975|-82.287",
    "57.427|-110.793",
    "49.211|-122.913",
    "45.304|-65.956",
    "43.866|-79.841",
    "45.4|-72.725",
    "53.64|-113.633",
    "42.861|-80.355",
    "50.041|-110.698",
    "55.167|-118.806",
    "51.286|-114.025",
    "43.634|-79.982",
    "49.263|-122.751",
    "45.933|-66.644",
    "45.69|-73.856",
    "45.628|-72.938",
    "43.996|-79.448",
    "49.321|-123.068",
    "42.99|-79.249",
    "46.374|-79.43",
    "44.252|-77.364",
    "45.642|-74.065",
    "46.825|-73.012",
    "45.49|-73.823",
    "49.847|-99.955",
    "48.37|-68.482",
    "45.366|-73.74",
    "45.76|-73.597",
    "45.045|-74.724",
    "46.062|-71.975",
    "44.015|-79.322",
    "42.953|-79.881",
    "44.31|-79.387",
    "45.572|-73.948",
    "44.192|-77.565",
    "49.368|-123.17",
    "48.185|-78.925",
    "48.494|-81.297",
    "45.591|-73.419",
    "43.138|-80.736",
    "45.267|-74.023",
    "50.217|-119.386",
    "42.775|-81.175",
    "49.217|-122.346",
    "45.383|-74.046",
    "43.088|-80.452",
    "42.24|-82.552",
    "44.268|-79.592",
    "46.26|-63.125",
    "53.203|-105.725",
    "48.448|-123.535",
    "44.116|-79.623",
    "46.015|-73.116",
    "44.082|-79.775",
    "53.547|-113.914",
    "50.402|-105.55",
    "49.489|-119.572",
    "49.281|-122.879",
    "49.899|-119.582",
    "49.983|-125.271",
    "46.104|-70.682",
    "48.027|-77.755",
    "45.47|-73.668",
    "43.372|-80.985",
    "45.457|-73.816",
    "44.613|-79.412",
    "48.612|-71.683",
    "42.919|-79.045",
    "42.218|-83.05",
    "53.261|-113.53",
    "45.599|-73.328",
    "48.835|-123.709",
    "45.433|-73.288",
    "43.915|-80.114",
    "50.721|-113.966",
    "42.095|-82.556",
    "45.353|-73.598",
    "43.174|-79.564",
    "45.617|-73.86",
    "45.207|-72.147",
    "45.534|-73.344",
    "47.502|-52.955",
    "45.641|-73.833",
    "49.099|-122.66",
    "51.175|-114.466",
    "49.709|-124.974",
    "46.121|-71.297",
    "50.355|-66.107",
    "46.083|-64.712",
    "60.71|-135.075",
    "43.94|-77.162",
    "45.483|-75.212",
    "53.744|-113.149",
    "45.392|-73.416",
    "44.145|-79.381",
    "43.146|-79.439",
    "42.214|-82.954",
    "47.521|-52.813",
    "45.578|-73.216",
    "45.877|-73.412",
    "42.113|-83.042",
    "45.503|-73.507",
    "44.504|-80.267",
    "42.102|-82.732",
    "49.267|-68.256",
    "47.526|-52.889",
    "44.604|-75.701",
    "44.578|-80.914",
    "45.684|-73.388",
    "45.377|-73.51",
    "42.912|-81.555",
    "45.864|-73.784",
    "44.5|-80.009",
    "46.017|-73.423",
    "42.085|-82.897",
    "45.485|-73.602",
    "45.517|-73.646",
    "56.249|-120.846",
    "45.456|-73.855",
    "49.531|-115.758",
    "49.024|-122.79",
    "45.409|-74.163",
    "51.037|-113.837",
    "45.303|-79.277",
    "48.928|-58.014",
    "46.049|-64.815",
    "53.278|-110.03",
    "62.473|-114.384",
    "49.726|-123.117",
    "47.82|-69.518",
    "43.975|-78.152",
    "45.426|-73.886",
    "45.453|-73.737",
    "46.756|-71.505",
    "43.077|-79.225",
    "53.011|-112.837",
    "45.57|-73.166",
    "49.246|-122.69",
    "42.916|-79.191",
    "45.429|-65.929",
    "48.446|-123.31",
    "45.531|-73.938",
    "50.714|-119.236",
    "49.252|-124.797",
    "48.434|-123.408",
    "47.027|-65.503",
    "43.201|-79.123",
    "45.541|-73.903",
    "53.352|-113.415",
    "43.035|-81.451",
    "53.53|-113.993",
    "45.89|-77.316",
    "43.044|-79.337",
    "45.518|-73.278",
    "45.396|-73.565",
    "44.732|-79.902",
    "48.421|-123.493",
    "48.581|-123.422",
    "44.017|-78.39",
    "50.288|-107.795",
    "47.385|-68.346",
    "46.806|-71.358",
    "44.972|-75.645",
    "51.216|-102.464",
    "47.446|-64.978",
    "45.742|-74.151",
    "45.046|-79.236",
    "44.274|-77.005",
    "42.863|-80.735",
    "49.519|-96.682",
    "45.829|-73.916",
    "49.831|-94.429",
    "54.404|-110.262",
    "46.406|-63.781",
    "52.298|-114.115",
    "48.943|-64.564",
    "45.371|-73.985",
    "50.568|-111.9",
    "45.766|-73.83",
    "46.396|-80.086",
    "52.769|-108.275",
    "48.798|-67.474",
    "48.771|-72.215",
    "48.958|-55.704",
    "46.544|-75.625",
    "49.679|-124.918",
    "51.086|-115.351",
    "45.638|-73.801",
    "45.817|-77.111",
    "46.044|-73.473",
    "51.051|-113.389",
    "44.402|-81.363",
    "55.75|-97.848",
    "45.903|-73.323",
    "45.205|-72.778",
    "50.583|-113.863",
    "46.439|-70.999",
    "49.969|-98.286",
    "42.965|-81.051",
    "45.243|-76.28",
    "49.879|-124.542",
    "43.696|-80.98",
    "45.307|-73.742",
    "52.469|-113.72",
    "46.324|-72.33",
    "45.872|-74.057",
    "48.409|-123.684",
    "50.088|-119.406",
    "45.967|-74.124",
    "44.321|-77.803",
    "45.29|-73.882",
    "45.665|-74.304",
    "48.654|-77.934",
    "45.399|-74.981",
    "43.032|-80.881",
    "52.967|-113.386",
    "42.731|-81.093",
    "49.181|-97.938",
    "44.204|-80.901",
    "49.315|-124.317",
    "44.883|-79.336",
    "45.348|-63.271",
    "54.287|-130.311",
    "55.76|-120.238",
    "45.657|-73.304",
    "47.254|-61.957",
    "47.627|-65.58",
    "50.098|-122.989",
    "44.112|-77.759",
    "53.284|-109.986",
    "48.948|-54.553",
    "48.65|-123.407",
    "45.382|-65.979",
    "54.455|-128.572",
    "49.597|-119.686",
    "45.719|-75.68",
    "49.143|-102.987",
    "43.76|-80.135",
    "44.247|-81.49",
    "46.942|-70.521",
    "48.643|-123.434",
    "59.253|-116.599",
    "46.061|-73.759",
    "52.325|-106.582",
    "48.279|-74.438",
    "44.603|-80.743",
    "49.666|-103.847",
    "44.958|-75.253",
    "45.391|-73.959",
    "52.133|-122.152",
    "46.405|-82.633",
    "45.434|-73.161",
    "45.576|-75.765",
    "45.371|-73.915",
    "50.227|-119.194",
    "45.139|-76.144",
    "43.16|-81.896",
    "49.488|-117.293",
    "48.481|-123.47",
    "44.242|-65.149",
    "50.149|-96.89",
    "45.612|-74.62",
    "48.702|-72.454",
    "45.875|-74.187",
    "46.07|-74.287",
    "47.005|-71.852",
    "49.484|-123.793",
    "54.134|-115.65",
    "43.344|-81.406",
    "48.474|-72.234",
    "45.96|-73.741",
    "47.459|-79.711",
    "53.386|-117.593",
    "52.988|-122.477",
    "53.8|-113.639",
    "46.177|-64.995",
    "44.297|-80.53",
    "46.217|-63.096",
    "46.163|-74.583",
    "52.291|-106.658",
    "45.673|-73.761",
    "45.418|-73.347",
    "44.179|-81.247",
    "45.825|-64.204",
    "45.668|-73.783",
    "52.388|-113.802",
    "46.052|-73.405",
    "46.78|-71.691",
    "45.835|-66.502",
    "51.792|-114.125",
    "43.602|-81.307",
    "45.932|-74.003",
    "45.59|-62.643",
    "45.296|-72.681",
    "44.79|-79.915",
    "49.343|-124.428",
    "45.289|-72.977",
    "43.434|-81.225",
    "45.427|-76.358",
    "44.895|-76.017",
    "45.084|-71.863",
    "43.913|-80.888",
    "49.192|-98.106",
    "44.018|-80.061",
    "48.989|-123.823",
    "44.378|-64.517",
    "51.15|-100.04",
    "49.796|-112.151",
    "45.537|-73.214",
    "44.811|-81.204",
    "53.584|-116.461",
    "47.139|-71.41",
    "49.395|-82.412",
    "47.772|-70.055",
    "45.473|-76.686",
    "49.724|-112.617",
    "46.216|-72.603",
    "47.644|-52.827",
    "54.062|-128.668",
    "44.081|-80.197",
    "53.346|-60.499",
    "45.257|-73.634",
    "49.276|-117.654",
    "51.413|-112.643",
    "48.209|-80.079",
    "45.247|-74.29",
    "47.659|-52.76",
    "45.818|-73.264",
    "45.687|-75.979",
    "51.174|-115.568",
    "52.03|-113.959",
    "46.98|-71.296",
    "43.016|-82.089",
    "45.485|-74.37",
    "49.792|-92.772",
    "63.76|-68.46",
    "48.621|-93.389",
    "49.075|-117.732",
    "46.833|-71.63",
    "44.153|-81.024",
    "45.639|-72.539",
    "43.736|-81.708",
    "46.913|-71.148",
    "43.669|-81.476",
    "50.984|-118.188",
    "48.328|-64.813",
    "49.88|-74.252",
    "42.772|-80.987",
    "45.374|-73.544",
    "49.66|-115.982",
    "42.74|-80.788",
    "47.045|-71.148",
    "48.821|-79.227",
    "43.254|-81.143",
    "53.208|-114.985",
    "52.676|-113.581",
    "52.961|-66.937",
    "46.691|-71.711",
    "45.8|-66.605",
    "46.255|-72.935",
    "47.412|-70.715",
    "50.114|-120.784",
    "43.448|-81.611",
    "45.672|-74.452",
    "45.301|-74.202",
    "44.464|-80.396",
    "45.481|-73.647",
    "45.356|-72.589",
    "45.531|-75.867",
    "48.002|-66.634",
    "56.227|-117.316",
    "44.402|-81.2",
    "49.78|-67.272",
    "45.774|-71.929",
    "45.342|-74.113",
    "45.534|-74.014",
    "46.2|-64.516",
    "55.278|-114.776",
    "46.58|-71.253",
    "52.377|-114.924",
    "48.557|-58.562",
    "53.354|-113.726",
    "46.22|-71.775",
    "43.839|-66.106",
    "49.133|-66.332",
    "45.498|-73.975",
    "45.35|-80.037",
    "43.149|-81.636",
    "45.344|-73.456",
    "46.173|-73.43",
    "48.174|-54.031",
    "46.231|-70.775",
    "48.584|-68.189",
    "45.203|-78.404",
    "45.072|-64.519",
    "52.839|-110.845",
    "47.733|-65.867",
    "49.371|-121.468",
    "48.48|-67.43",
    "46.358|-66.997",
    "46.601|-71.517",
    "49.258|-121.837",
    "45.955|-73.881",
    "44.48|-77.273",
    "46.9|-71.554",
    "47.576|-53.316",
    "46.173|-71.886",
    "52.862|-104.597",
    "52.319|-112.719",
    "49.134|-97.723",
    "44.901|-76.251",
    "48.415|-89.506",
    "45.726|-73.49",
    "45.94|-73.401",
    "45.408|-72.986",
    "52.202|-105.121",
    "45.597|-76.216",
    "45.776|-73.354",
    "53.988|-111.282",
    "48.533|-71.11",
    "46.471|-72.67",
    "42.884|-82.135",
    "42.78|-81.649",
    "53.498|-112.059",
    "45.547|-73.233",
    "45.587|-70.884",
    "44.025|-81.215",
    "46.688|-71.059",
    "45.521|-72.896",
    "50.074|-110.78",
    "49.579|-114.397",
    "45.254|-72.538",
    "45.85|-73.48",
    "45.644|-75.475",
    "45.25|-73.801",
    "49.756|-119.767",
    "45.57|-72.006",
    "54.268|-110.734",
    "54.774|-127.156",
    "44.686|-78.433",
    "45.38|-71.635",
    "53.857|-101.223",
    "45.274|-74.242",
    "49.108|-116.517",
    "46.234|-63.196",
    "54.122|-108.442",
    "45.916|-64.394",
    "47.045|-67.756",
    "49.122|-81.018",
    "47.137|-55.167",
    "50.05|-92.096",
    "51.663|-114.136",
    "49.509|-115.057",
    "49.2|-57.332",
    "45.399|-73.223",
    "46.153|-67.589",
    "45.457|-74.162",
    "44.333|-76.174",
    "45.859|-73.587",
    "45.806|-66.381",
    "50.447|-119.197",
    "50.432|-119.266",
    "54.156|-113.841",
    "49.031|-119.469",
    "49.689|-83.659",
    "45.453|-73.651",
    "46.236|-81.754",
    "42.577|-81.655",
    "54.778|-101.839",
    "45.322|-66.226",
    "45.424|-73.941",
    "48.776|-123.692",
    "49.183|-119.548",
    "45.835|-72.599",
    "46.043|-74.199",
    "47.638|-68.868",
    "47.731|-53.24",
    "46.322|-70.815",
    "46.171|-66.516",
    "46.526|-72.839",
    "58.998|-123.937",
    "50.134|-97.328",
    "47.859|-64.615",
    "47.468|-65.847",
    "46.228|-64.641",
    "45.97|-73.265",
    "45.998|-64.609",
    "44.415|-77.443",
    "46.239|-79.277",
    "45.922|-72.407",
    "48.384|-123.564",
    "46.146|-73.874",
    "49.741|-87.016",
    "45.957|-72",
    "49.604|-97.059",
    "50.229|-99.462",
    "49.404|-123.514",
    "52.888|-118.022",
    "54.124|-114.402",
    "51.467|-109.156",
    "50.931|-102.818",
    "46.418|-72.778",
    "48.711|-80.809",
    "45.484|-73.227",
    "45.997|-64.952",
    "46.241|-73.53",
    "54.016|-124.015",
    "52.734|-108.317",
    "45.174|-67.31",
    "45.341|-72.527",
    "53.361|-104.011",
    "46.727|-71.6",
    "45.622|-61.997",
    "45.365|-72.194",
    "46.536|-75.032",
    "45.523|-65.838",
    "47.707|-65.715",
    "45.722|-65.51",
    "46.553|-71.444",
    "47.764|-64.963",
    "44.718|-75.521",
    "49.106|-97.567",
    "45.562|-62.67",
    "45.089|-64.37",
    "46.082|-73.189",
    "45.884|-66.676",
    "45.91|-74.254",
    "50.704|-127.447",
    "47.006|-71.056",
    "47.38|-70.032",
    "46.05|-77.417",
    "51.082|-93.786",
    "53.354|-110.846",
    "45.223|-77.938",
    "51.562|-114.096",
    "48.175|-66.188",
    "47.605|-59.109",
    "45.438|-72.107",
    "49.032|-118.439",
    "47.744|-69.474",
    "52.11|-101.255",
    "45.084|-72.56",
    "45.142|-81.426",
    "48.404|-71.844",
    "45.963|-73.578",
    "45.978|-73.495",
    "44.626|-77.724",
    "46.627|-70.987",
    "46.313|-64.74",
    "45.188|-73.404",
    "46.322|-74.228",
    "45.047|-77.735",
    "42.67|-81.496",
    "46.176|-79.411",
    "46.078|-73.568",
    "49.931|-98.833",
    "46.38|-75.98",
    "45.625|-73.52",
    "45.334|-65.769",
    "47.088|-70.335",
    "45.773|-72.054",
    "45.492|-74.048",
    "45.42|-73.909",
    "46.395|-70.514",
    "45.489|-72.64",
    "49.766|-114.825",
    "48.577|-71.328",
    "50.018|-113.584",
    "49.634|-125.041",
    "47.076|-70.922",
    "45.72|-75.057",
    "49.126|-117.858",
    "55.317|-123.159",
    "49.462|-112.662",
    "51.297|-116.963",
    "48.214|-65.787",
    "46.951|-71.125",
    "49.37|-123.373",
    "46.735|-72.557",
    "45.482|-71.663",
    "44.989|-64.125",
    "49.49|-113.947",
    "47.244|-65.282",
    "45.553|-62.708",
    "49.015|-57.56",
    "45.847|-74.137",
    "49.229|-124.098",
    "45.112|-73.986",
    "46.208|-70.477",
    "49.192|-113.308",
    "53.878|-119.138",
    "47.942|-66.697",
    "45.317|-75.092",
    "60.816|-115.849",
    "45.824|-65.569",
    "45.954|-74.353",
    "46.08|-74.472",
    "47.288|-53.828",
    "43.792|-81.301",
    "46.442|-82.939",
    "47.529|-69.786",
    "50.449|-63.369",
    "46.054|-79.342",
    "48.616|-53.106",
    "45.848|-73.344",
    "45.13|-72.787",
    "49.244|-55.076",
    "48.435|-64.531",
    "47.203|-70.239",
    "46.702|-71.782",
    "50.507|-116.032",
    "46.113|-65.206",
    "47.082|-71.633",
    "51.103|-97.17",
    "48.147|-78.078",
    "46.577|-70.863",
    "45.001|-78.113",
    "49.854|-100.933",
    "46.17|-67.102",
    "46.474|-72.529",
    "52.138|-113.873",
    "48.747|-86.314",
    "46.016|-73.346",
    "48.125|-69.16",
    "68.385|-133.748",
    "47.157|-70.84",
    "46.048|-70.51",
    "52.85|-104.05",
    "45.665|-72.145",
    "48.826|-124.046",
    "50.065|-96.509",
    "51.303|-101.353",
    "45.621|-61.352",
    "51.703|-113.262",
    "45.838|-73.519",
    "46.735|-71.913",
    "45.685|-62.709",
    "45.194|-73.605",
    "49.508|-98.006",
    "48.097|-65.287",
    "46.179|-73.706",
    "53.819|-113.335",
    "58.511|-117.152",
    "45.457|-71.76",
    "49.021|-55.499",
    "50.285|-98.858",
    "45.226|-71.804",
    "48.053|-66.393",
    "45.508|-73.117",
    "48.539|-64.374",
    "50.44|-104.358",
    "45.328|-72.821",
    "47|-70.416",
    "47.719|-70.243",
    "48.782|-69.133",
    "46.526|-64.752",
    "45.33|-73.15",
    "48.458|-68.396",
    "44.856|-75.814",
    "45.658|-72.763",
    "49.444|-98.628",
    "48.816|-72.532",
    "46.011|-71.878",
    "45.576|-74.324",
    "56.071|-118.381",
    "47.675|-53.279",
    "54.397|-126.628",
    "46.148|-73.531",
    "51.427|-114.031",
    "46.738|-73.31",
    "49.509|-56.077",
    "49.72|-113.4",
    "54.716|-113.288",
    "50.551|-119.146",
    "45.972|-77.51",
    "43.952|-80.367",
    "45.56|-71.789",
    "45.901|-74.115",
    "46.81|-70.993",
    "45.436|-66.061",
    "46.672|-72.035",
    "48.014|-84.759",
    "45.582|-73.065",
    "45.429|-72.873",
    "46.585|-71.104",
    "47.048|-70.964",
    "49.133|-55.376",
    "46.007|-74.176",
    "48.382|-76.187",
    "47.547|-68.579",
    "62.823|-92.124",
    "46.309|-72.828",
    "51.995|-101.416",
    "49.353|-120.522",
    "45.712|-74.679",
    "45.884|-66.867",
    "45.598|-75.243",
    "45.451|-65.838",
    "46.043|-71.125",
    "48.468|-71.596",
    "48.544|-68.299",
    "48.654|-88.695",
    "45.019|-72.096",
    "46.091|-73.439",
    "46.048|-73.049",
    "48.645|-71.016",
    "46.24|-67.598",
    "46.055|-74.098",
    "45.447|-73.053",
    "58.146|-68.37",
    "48.761|-91.62",
    "48.588|-72.369",
    "48.763|-78.999",
    "50.028|-99.464",
    "50.146|-101.665",
    "46.562|-75.349",
    "51.801|-114.65",
    "56.192|-117.608",
    "45.933|-81.94",
    "48.056|-65.44",
    "46.832|-75.622",
    "45.459|-80.031",
    "50.69|-114.227",
    "45.344|-72.906",
    "55.114|-105.282",
    "45.704|-71.448",
    "49.741|-112.922",
    "46.257|-71.737",
    "46.151|-80.526",
    "61.115|-94.164",
    "46.494|-80.363",
    "47.617|-53.351",
    "45.114|-73.767",
    "46.314|-73.386",
    "46.298|-73.33",
    "46.772|-71.841",
    "45.092|-74.358",
    "55.349|-118.776",
    "45.608|-73.253",
    "48.2|-66.035",
    "45.315|-73.671",
    "45.698|-66.826",
    "45.052|-73.367",
    "47.331|-79.436",
    "47.521|-69.295",
    "47.736|-64.713",
    "50.317|-122.886",
    "46.542|-71.638",
    "52.441|-109.164",
    "52.639|-114.237",
    "55.438|-116.499",
    "49.621|-100.298",
    "45.121|-72.983",
    "51.644|-111.924",
    "50.671|-114.277",
    "45.574|-72.828",
    "60.04|-112.213",
    "45.762|-72.497",
    "45.676|-73.062",
    "49.133|-97.087",
    "46.485|-71.394",
    "45.651|-65.548",
    "46.602|-71.704",
    "45.046|-64.737",
    "55.722|-121.644",
    "50.655|-102.072",
    "50.055|-114.86",
    "48.342|-71.677",
    "46.857|-72.594",
    "45.234|-72.051",
    "46.266|-74.763",
    "45.952|-70.668",
    "49.05|-66.69",
    "45.615|-62.632",
    "52.784|-67.325",
    "45.521|-73.002",
    "45.233|-73.111",
    "55.211|-119.424",
    "47.331|-53.161",
    "46.094|-75.997",
    "45.946|-73.076",
    "51.555|-107.993",
    "50.248|-99.834",
    "46.148|-70.918",
    "45.088|-74.179",
    "50.737|-101.37",
    "46.601|-78.888",
    "50.836|-118.978",
    "46.217|-64.276",
    "42.844|-81.92",
    "46.403|-71.091",
    "46.053|-70.948",
    "46.968|-69.801",
    "46.755|-70.94",
    "46.784|-70.766",
    "49.632|-105.991",
    "49.418|-112.864",
    "56.496|-109.437",
    "47.669|-64.891",
    "46.472|-64.746",
    "44.702|-66.815",
    "46.681|-73.955",
    "49.178|-100.094",
    "46.521|-71.078",
    "49.161|-98.513",
    "45.357|-66.852",
    "50.595|-127.159",
    "45.902|-71.358",
    "46.093|-72.361",
    "47.641|-65.185",
    "51.651|-120.019",
    "46.48|-71.151",
    "46.21|-73.037",
    "45.339|-73.803",
    "47.069|-55.159",
    "47.089|-55.77",
    "45.75|-73.133",
    "45.259|-72.835",
    "46.09|-66.059",
    "48.372|-67.228",
    "50.822|-119.689",
    "46.046|-76.725",
    "46.037|-65.049",
    "46.089|-73.234",
    "51.487|-107.059",
    "50.683|-121.903",
    "45.527|-72.054",
    "47.31|-66.266",
    "44.379|-64.326",
    "48.913|-72.395",
    "51.382|-55.629",
    "49.676|-54.134",
    "45.601|-73.093",
    "53.264|-113.807",
    "52.064|-107.979",
    "48.519|-123.504",
    "45.304|-74.312",
    "47.634|-52.686",
    "46.046|-67.605",
    "46.624|-72.071",
    "49.354|-122.854",
    "48.256|-64.959",
    "45.844|-70.597",
    "47.004|-65.063",
    "46.223|-71.082",
    "49.636|-54.74",
    "47.51|-67.389",
    "46.266|-73.803",
    "46.423|-73.361",
    "45.9|-73.17",
    "49.053|-76.991",
    "49.168|-53.595",
    "45.693|-73.226",
    "45.221|-66.682",
    "45.496|-72.315",
    "51.078|-98.458",
    "45.491|-72.754",
    "47.377|-67.551",
    "45.315|-73.538",
    "46.652|-67.084",
    "46.728|-70.84",
    "47.641|-52.936",
    "46.11|-72.827",
    "46.39|-75.035",
    "50.48|-104.412",
    "49.975|-100.277",
    "50.349|-113.771",
    "45.298|-71.875",
    "49.67|-96.655",
    "47.688|-69.586",
    "45.275|-71.943",
    "45.046|-74.096",
    "45.641|-75.032",
    "45.225|-74.332",
    "46.385|-73.544",
    "45.646|-72.682",
    "50.373|-100.97",
    "48.53|-71.794",
    "45.701|-82.193",
    "49.905|-109.475",
    "48.695|-54.058",
    "53.373|-112.662",
    "46.104|-71.612",
    "48.589|-71.533",
    "48.478|-70.825",
    "47.736|-52.776",
    "64.331|-96.14",
    "45.211|-73.317",
    "44.621|-65.762",
    "48.167|-89.534",
    "53.953|-113.114",
    "46.084|-73.106",
    "45.223|-73.211",
    "42.994|-82.404",
    "47.422|-65.478",
    "46.616|-65.755",
    "50.766|-103.799",
    "48.136|-65.688",
    "51.634|-102.437",
    "46.602|-72.2",
    "48.561|-58.63",
    "52.355|-110.263",
    "46.656|-65.048",
    "50.464|-121.014",
    "46.313|-78.713",
    "46.905|-71.04",
    "55.011|-121.05",
    "48.724|-71.702",
    "45.392|-73.986",
    "49.872|-111.379",
    "51.638|-121.329",
    "45.145|-73.276",
    "48.807|-54.241",
    "46.388|-64.862",
    "54.407|-116.801",
    "48.431|-77.669",
    "45.91|-73.678",
    "46.063|-72.881",
    "45.305|-66.371",
    "46.168|-62.654",
    "46.884|-71.606",
    "45.15|-73.519",
]


def fetch_data():
    locs = ["https://www.dairyqueen.com/en-ca/locations/on/ajax/250-bayly-st-w/1993/"]
    for lat, lng in search:
        time.sleep(1)
        url = (
            "https://prod-dairyqueen.dotcmscloud.com/api/vtl/locations?country=ca&lat="
            + str(lat)
            + "&long="
            + str(lng)
        )
        session = SgRequests()
        r = session.get(url, headers=headers)
        logger.info(str(lat) + "-" + str(lng))
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"address1":"' in line:
                items = line.split('"address1":"')
                for item in items:
                    if '"url":"' in item:
                        lurl = (
                            "https://www.dairyqueen.com/en-ca"
                            + item.split('"url":"')[1].split('"')[0]
                        )
                        if lurl not in locs:
                            locs.append(lurl)
    for coord in allcities:
        lat = coord.split("|")[0]
        lng = coord.split("|")[1]
        time.sleep(1)
        url = (
            "https://prod-dairyqueen.dotcmscloud.com/api/vtl/locations?country=ca&lat="
            + lat
            + "&long="
            + lng
        )
        session = SgRequests()
        r = session.get(url, headers=headers)
        logger.info(lat + "-" + lng)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"address3":"' in line:
                items = line.split('"address3":"')
                for item in items:
                    if '"url":"' in item:
                        lurl = (
                            "https://www.dairyqueen.com/en-ca"
                            + item.split('"url":"')[1].split('"')[0]
                        )
                        if lurl not in locs:
                            locs.append(lurl)
    website = "dairyqueen.ca"
    typ = "<MISSING>"
    country = "CA"
    for loc in locs:
        PFound = False
        count = 0
        while PFound is False:
            count = count + 1
            loc = loc + "/"
            loc = loc.replace("https://", "HTTPS")
            loc = loc.replace("//", "/")
            loc = loc.replace("HTTPS", "https://")
            Closed = False
            logger.info(loc)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = loc.rsplit("/", 2)[1]
            phone = ""
            lat = ""
            lng = ""
            hours = ""
            session = SgRequests()
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if "this page doesn't exist" in line2:
                    Closed = True
                if '<h1 class="my-1 h2">' in line2:
                    name = line2.split('<h1 class="my-1 h2">')[1].split("<")[0]
                if '"address3":"' in line2:
                    add = line2.split('"address3":"')[1].split('"')[0]
                    PFound = True
                    lat = line2.split('"latlong":"')[1].split(",")[0]
                    lng = line2.split('"latlong":"')[1].split(",")[1].replace('"', "")
                    city = line2.split('"city":"')[1].split('"')[0]
                    state = line2.split('"stateProvince":"')[1].split('"')[0]
                    try:
                        zc = line2.split('"postalCode":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    try:
                        phone = line2.split('"phone":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                if '"miniSite":{"miniSiteHours":"' in line2:
                    days = (
                        line2.split('"miniSite":{"miniSiteHours":"')[1]
                        .split('","')[0]
                        .split(",")
                    )
                    for day in days:
                        dnum = day.split(":")[0]
                        if dnum == "1":
                            hrs = "Sunday: " + day.split(":", 1)[1]
                        if dnum == "2":
                            hrs = "Monday: " + day.split(":", 1)[1]
                        if dnum == "3":
                            hrs = "Tuesday: " + day.split(":", 1)[1]
                        if dnum == "4":
                            hrs = "Wednesday: " + day.split(":", 1)[1]
                        if dnum == "5":
                            hrs = "Thursday: " + day.split(":", 1)[1]
                        if dnum == "6":
                            hrs = "Friday: " + day.split(":", 1)[1]
                        if dnum == "7":
                            hrs = "Saturday: " + day.split(":", 1)[1]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            name = name.replace("&amp;", "&").replace("&amp", "&")
            add = add.replace("&amp;", "&").replace("&amp", "&")
            add = add.replace("\\u0026", "&")
            if Closed is False:
                city = city.replace("\\u0026apos;", "'")
                add = add.replace("\\u0026apos;", "'")
                name = name.replace("\\u0026apos;", "'")
                yield SgRecord(
                    locator_domain=website,
                    page_url=loc,
                    location_name=name,
                    street_address=add,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code=country,
                    phone=phone,
                    location_type=typ,
                    store_number=store,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )
            if count >= 3:
                PFound = True


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
