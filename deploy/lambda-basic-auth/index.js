exports.handler = async (event) => {
  const request = event.Records[0].cf.request;
  const headers = request.headers;
  const authHeader = headers.authorization ? headers.authorization[0].value : '';

  const user = 'admin';
  const pass = 'changeme';
  const expected = 'Basic ' + Buffer.from(user + ':' + pass).toString('base64');

  if (authHeader !== expected) {
    return {
      status: '401',
      statusDescription: 'Unauthorized',
      body: 'Unauthorized',
      headers: {
        'www-authenticate': [{ key: 'WWW-Authenticate', value: 'Basic realm="Docs"' }]
      }
    };
  }

  if (request.uri.endsWith('/')) {
    request.uri += 'index.html';
  } else if (!request.uri.includes('.')) {
    request.uri += '/index.html';
  }

  return request;
};
