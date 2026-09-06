let currentAccount = "";

addEventListener("fetch", (event) => {
  event.respondWith(handle(event.request));
});

async function handle(request: Request): Promise<Response> {
  currentAccount = request.headers.get("X-Account") ?? "anonymous";
  void fetch("https://telemetry.acme.com/events", {
    method: "POST",
    body: JSON.stringify({ account: currentAccount }),
  });
  return new Response(currentAccount);
}
