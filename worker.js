export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let path = url.pathname;

    if (path === "/" || path === "") {
      path = "/index.html";
    }

    if (!path.includes(".")) {
      path = path + ".html";
    }

    try {
      const asset = await env.ASSETS.fetch(path);
      return asset;
    } catch (e) {
      return new Response("Not Found", { status: 404 });
    }
  },
};
