import { test, expect } from "@playwright/test";
test("inicio, buscador y ficha reales", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Iniciar recorrido" }).click();
  await expect(
    page.getByRole("heading", { name: "Explorar León", exact: true }),
  ).toBeVisible();
  await page.getByLabel("Buscar un lugar").fill("catedral");
  await expect(page.locator(".grid .card")).toHaveCount(1);
  await page.getByRole("link", { name: "Explorar ficha" }).click();
  await expect(
    page.getByRole("heading", { name: "Catedral de León", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Revisado con fuentes", { exact: true }),
  ).toBeVisible();
});
test("filtro municipal y ruta digital reales", async ({ page }) => {
  await page.goto("/explorar");
  await page
    .getByLabel("Municipio", { exact: true })
    .selectOption("La Paz Centro");
  await expect(page.locator(".grid .card")).toHaveCount(1);
  await page.goto("/rutas/origenes");
  await expect(page.getByText("Parada 1 de 2")).toBeVisible();
  await page.getByRole("button", { name: "Siguiente parada" }).click();
  await expect(page.getByText("Parada 2 de 2")).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Catedral de León", exact: true }),
  ).toBeVisible();
});
test("actividad calificada por la API real", async ({ page }) => {
  await page.goto("/actividad");
  await page.getByLabel("Como investigación por verificar").check();
  await page.getByLabel("Mediante la lista de lugares").check();
  await page.getByLabel("1524", { exact: true }).check();
  await page.getByLabel("Rubén Darío", { exact: true }).check();
  await page.getByRole("button", { name: "Finalizar actividad" }).click();
  await expect(
    page.getByRole("heading", { name: "Resultado: 4 de 4" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Repetir actividad" }).click();
  await page.getByLabel("Como un hecho histórico demostrado").check();
  await page.getByLabel("No se pueden consultar").check();
  await page.getByLabel("1967", { exact: true }).check();
  await page.getByLabel("José de la Cruz Mena", { exact: true }).check();
  await page.getByRole("button", { name: "Finalizar actividad" }).click();
  await expect(
    page.getByRole("heading", { name: "Resultado: 0 de 4" }),
  ).toBeVisible();
});
test("línea del tiempo declara el contenido pendiente", async ({ page }) => {
  await page.route("**/api/events/", (route) => route.fulfill({ json: [] }));
  await page.goto("/tiempo");
  await expect(
    page.getByText("Aún no hay acontecimientos con fechas verificadas.", {
      exact: false,
    }),
  ).toBeVisible();
});
test("mapa, mosaicos fallidos y línea del tiempo con datos reales del catálogo", async ({
  page,
}) => {
  await page.route("https://*.tile.openstreetmap.org/**", (route) =>
    route.abort(),
  );
  await page.goto("/explorar");
  await expect(page.locator(".place-marker")).toHaveCount(2);
  await page.locator(".place-marker").first().click();
  await page
    .locator(".leaflet-popup")
    .getByRole("link", { name: "Abrir ficha" })
    .click();
  await expect(
    page.getByRole("heading", {
      name: /Catedral de León|Ruinas de León Viejo/,
      level: 1,
    }),
  ).toBeVisible();
  await page.goto("/tiempo");
  await expect(page.locator(".timeline li")).toHaveCount(4);
  await page
    .getByRole("link", { name: "Abrir ficha de Catedral de León" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Catedral de León", exact: true }),
  ).toBeVisible();
});
test("error de API recuperable", async ({ page }) => {
  await page.route("**/api/places/", (route) =>
    route.fulfill({ status: 503, json: { detail: "Fallo de prueba" } }),
  );
  await page.goto("/explorar");
  await expect(page.getByRole("alert")).toBeVisible();
  await page.unroute("**/api/places/");
  await page.getByRole("button", { name: "Reintentar" }).click();
  await expect(page.locator(".grid .card")).toHaveCount(8);
});
test("móvil y QR generado localmente", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/explorar");
  await expect(page.locator(".grid .card")).toHaveCount(8);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.goto("/feria");
  await page
    .getByLabel("Dirección de inicio o de una ruta")
    .fill("https://example.org/rutas/origenes");
  await page.getByRole("button", { name: "Generar QR" }).click();
  await expect(
    page.getByRole("img", {
      name: "Código QR de la dirección de la demostración",
    }),
  ).toBeVisible();
  await page
    .getByLabel("Dirección de inicio o de una ruta")
    .fill("http://localhost:5173");
  await page.getByRole("button", { name: "Generar QR" }).click();
  await expect(page.getByRole("alert")).toContainText("no localhost");
});
