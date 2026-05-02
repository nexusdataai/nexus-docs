// CloudFront Function (viewer-request) for NexusAI docs.
// Rewrites directory-style URLs to the underlying index.html object so that
// MkDocs `use_directory_urls: true` works against a private S3 origin.
//   /                  -> /index.html
//   /business/         -> /business/index.html
//   /business/ai-stack -> /business/ai-stack/index.html
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    if (uri.endsWith('/')) {
        request.uri = uri + 'index.html';
    } else if (!uri.split('/').pop().includes('.')) {
        request.uri = uri + '/index.html';
    }

    return request;
}
