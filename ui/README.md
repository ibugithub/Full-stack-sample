# Template UI

This Next.js App Router application is part of the single Django deployment.
It exports static HTML and assets to `out/`; Django at the repository root serves
them. Do not deploy a separate Next.js server or use `next start`.

Run `npm ci` to install dependencies and `npm run build` to export the UI.
Leave `NEXT_PUBLIC_BACKEND_BASE_URL` blank for the combined deployment. Public
variables are compiled into the build, so rebuild after changing them.

For local hot reload, set the backend URL to `http://localhost:8000` in `.env`
and run `npm run dev`. This is an optional development workflow only.

The retained screens are the neutral homepage, account access/recovery, profiles,
password changes, social callbacks and staff user listing. Shared components,
Redux auth state, toast notifications and the API client are reusable.

Optional social sign-in buttons appear only when their public client IDs are
configured. Never put provider secrets in a `NEXT_PUBLIC_` variable.

See the root README for combined setup, deployment, database notes and tests.
