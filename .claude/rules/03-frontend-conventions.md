# Frontend Conventions (JavaScript/CSS)

## Architecture
- **No framework** — Vanilla JS with modular file organization
- Files in `public/js/`, loaded via `<script>` tags in `index.html`
- Shared utilities: `config.js`, `utils.js`, `api.js`
- Feature modules: `products.js`, `news.js`, `cart.js`, `admin.js`

## JavaScript Patterns
- Use `Config.*` for constants (defined in `config.js`) — don't duplicate constants locally
- Use `Utils.*` for utilities (escapeHtml, formatCurrency, getStorage, etc.)
- Use `ApiClient.*` for API calls (has retry logic, timeouts) — don't use raw `fetch`
- Use `Utils.getStorage()`/`Utils.setStorage()` for localStorage — handles errors in private browsing
- i18n strings in `public/js/i18n.js` (Vietnamese)

## CSS / Styling
- **Tailwind CSS** via CDN — use utility classes in HTML
- Custom styles in `public/css/styles.css` for things Tailwind can't handle
- Follow the design system colors and typography (see `04-design-system.md`)
- Mobile-first responsive design

## HTML Components
- Reusable HTML partials in `public/components/` (header, footer, hero)
- SSR pages: Django views inject data into HTML templates
- Client-side pages: JS fetches data from `/api/*` endpoints

## Naming
- Files: kebab-case or camelCase (`image-handler.js`, `admin.js`)
- Functions: camelCase (`loadProducts`, `formatCurrency`)
- Constants: UPPER_SNAKE_CASE (`PRODUCTS_PER_PAGE`)
- DOM classes: Tailwind utilities or kebab-case custom classes

## Important
- XSS prevention: always use `Utils.escapeHtml()` for user content
- Image errors: `image-handler.js` provides fallback placeholder
- Cart state: persisted in localStorage
