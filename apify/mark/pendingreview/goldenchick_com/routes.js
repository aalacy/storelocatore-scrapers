const Apify = require('apify');

const enqueueStatePages = async ({ $ }, { requestQueue }) => Apify.utils.enqueueLinks({
  $,
  requestQueue,
  pseudoUrls: [
    'http://locations.goldenchick.com/[[a-z]][[a-z]]/',
  ],
  baseUrl: 'http://locations.goldenchick.com',
  userData: {
    urlType: 'state',
  },
});

const enqueueCityPages = async ({ $ }, { requestQueue }) => Apify.utils.enqueueLinks({
  $,
  requestQueue,
  pseudoUrls: [
    'http://locations.goldenchick.com/[[a-z]][[a-z]]/[(\\w|-)+]/',
  ],
  baseUrl: 'http://locations.goldenchick.com',
  userData: {
    urlType: 'city',
  },
});

const enqueueDetailPages = async ({ $ }, { requestQueue }) => Apify.utils.enqueueLinks({
  $,
  requestQueue,
  pseudoUrls: [
    'http://locations.goldenchick.com/[[a-z]][[a-z]]/[(\\w|-)+]/[(\\w|-)+]/',
  ],
  baseUrl: 'http://locations.goldenchick.com',
  userData: {
    urlType: 'detail',
  },
});

module.exports = {
  enqueueStatePages,
  enqueueCityPages,
  enqueueDetailPages,
};
