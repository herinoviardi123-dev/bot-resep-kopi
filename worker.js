import { getAssetFromKV } from '@cloudflare/kv-asset-handler';
export default {
  async fetch(request, env, ctx) {
    try {
      return await getAssetFromKV({ request, waitUntil: ctx.waitUntil.bind(ctx) }, { ASSET_NAMESPACE: env.__STATIC_CONTENT, ASSET_MANIFEST: env.__STATIC_CONTENT_MANIFEST });
    } catch (e) {
      const url = new URL(request.url);
      try {
        const indexRequest = new Request(url.origin + '/index.html', request);
        return await getAssetFromKV({ request: indexRequest, waitUntil: ctx.waitUntil.bind(ctx) }, { ASSET_NAMESPACE: env.__STATIC_CONTENT, ASSET_MANIFEST: env.__STATIC_CONTENT_MANIFEST });
      } catch (e2) {
        return new Response('Hey Kopi - Not Found', { status: 404 });
      }
    }
  }
};
