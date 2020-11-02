const Apify = require('apify');
const axios = require('axios');
const { Poi } = require('./Poi');

// extract url to common.js to find client credentials
function queryScriptFile($) {
  const scripts = $('script[src]');
  let srcUrl = null;
  scripts.each(function (idx) {
    const src = $(this).attr('src');
    if (src.match(/commons/)) {
      srcUrl = src;
    }
  });
  return srcUrl;
}

// fetch js file and extract credentials from code
async function queryCredentials(commonSrcUrl) {
  const { data } = await axios.get(commonSrcUrl);
  const matches = data.match(/\{(client.*?)\}/);
  if (!matches || !matches[1]) {
    throw new Error('Unable to extract client credentials from common file.');
  }

  // manual extraction since this is not in valid JSON format
  const [idKvp, secretKvp] = matches[1].split(',');
  const [idKey, idValue] = idKvp.split(':');
  const [secretKey, secretValue] = secretKvp.split(':');

  return {
    [idKey.trim()]: idValue.replace(/\'|\"/g, '').trim(),
    [secretKey.trim()]: secretValue.replace(/\'|\"/g, '').trim(),
  };
}

// recursively loop through paginations and fetch data.
async function queryAllStoreLocations(authToken, stores = [], nextUrl) {
  const currentPageUrl =
    nextUrl ||
    'https://api.koala.fuzzhq.com/v1/ordering/store-locations/?include[0]=operating_hours&per_page=50';

  const headers = {
    Authorization: `Bearer ${authToken}`,
  };
  try {
    const {
      data: { data, meta },
    } = await axios.get(currentPageUrl, { headers });

    stores.push(...data);
    const { next } = meta.pagination.links;

    if (next) {
      await queryAllStoreLocations(authToken, stores, next);
    }

    return stores;
  } catch (err) {
    console.log(err);
  }
}

// fetch authToken to make api query.
async function queryAuthToken(credentials) {
  const body = {
    ...credentials,
    grant_type: 'ordering_app_credentials',
    scope: 'group:ordering_app',
  };
  try {
    const { data } = await axios.post('https://api.koala.fuzzhq.com/oauth/access_token', body);
    return data.access_token;
  } catch (err) {
    throw new Error(`unable to fetch auth token: ${JSON.stringify(err, null, 2)}`);
  }
}

function formatPhone(phone) {
  if (!phone) {
    return null;
  }

  return phone.replace(/[\(|\)|-|+|\s]/g, '');
}

function formatHoursOfOperation(hours) {
  if (!hours || (hours && !hours.length)) {
    return null;
  }

  return hours.map((day) => ({
    start: new Date(day.start).toLocaleTimeString(),
    end: new Date(day.end).toLocaleTimeString(),
    day_of_week: day.day_of_week,
  }));
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  const locator_domain = 'pollotropical.com';
  const baseUrl = `https://www.${locator_domain}`;

  await requestQueue.addRequest({
    url: `${baseUrl}/locations`,
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    async handlePageFunction({ request, $ }) {
      const commonSrcUrl = queryScriptFile($);
      const credentials = await queryCredentials(`${baseUrl}${commonSrcUrl}`);
      const authToken = await queryAuthToken(credentials);
      const stores = await queryAllStoreLocations(authToken);
      const promises = stores.map((store) => {
        const {
          latitude,
          longitude,
          phone_number,
          operating_hours,
          street_address,
          city,
          zip_code: zip,
          brand_id: store_number,
          label: location_name,
          country: country_code,
          cached_data: { state },
        } = store;
        const poi = new Poi({
          locator_domain,
          city,
          state,
          zip,
          street_address,
          latitude,
          longitude,
          country_code,
          location_name,
          store_number,
          phone: formatPhone(phone_number),
          hours_of_operation: formatHoursOfOperation(operating_hours),
        });

        return Apify.pushData(poi);
      });

      await Promise.all(promises);
    },
  });

  await crawler.run();
});
