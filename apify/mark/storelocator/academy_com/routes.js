const Apify = require('apify');

const enqueueStatePages = async ({ page }, { requestQueue }) => Apify.utils.enqueueLinks({
  page,
  requestQueue,
  selectors: 'a',
  pseudoUrls: [
    'https://stores.academy.com/[[a-z]][[a-z]].html',
  ],
  userData: {
    urlType: 'state',
  },
});

const enqueueCityPages = async ({ page }, { requestQueue }) => Apify.utils.enqueueLinks({
  page,
  requestQueue,
  selectors: 'a',
  pseudoUrls: [
    'https://stores.academy.com/[[a-z]][[a-z]]/[(\\w|-)+].html',
  ],
  userData: {
    urlType: 'city',
  },
});

const enqueueDetailPages = async ({ page }, { requestQueue }) => Apify.utils.enqueueLinks({
  page,
  requestQueue,
  selectors: 'a',
  pseudoUrls: [
    'https://stores.academy.com/[[a-z]][[a-z]]/[.*]/[.*].html',
  ],
  userData: {
    urlType: 'detail',
  },
});

module.exports = {
  enqueueStatePages,
  enqueueCityPages,
  enqueueDetailPages,
};
