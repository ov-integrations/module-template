# Module tests

The `tests` directory contains the automated UI tests for the module. Tests are written in TypeScript and run with Playwright through the shared `@ov-integrations/playwright-framework` package.

## Directory structure

- `specs/` contains the Playwright test specifications and test metadata.
- `playwright.config.ts` contains the Playwright configuration. It uses the shared framework configuration, runs tests from `specs/`, and reads the application URL from `UI_TEST_WEB_URL`.
- `tsconfig.json` extends the TypeScript configuration provided by the shared Playwright framework.
- `package.json` and `package-lock.json` define and lock the test dependencies.
- `.npmrc` contains the npm configuration required to install dependencies.

The `specs/metadata.csv` file maps each test specification to the user account that should be used to run it. For example:

```csv
filename,username
ProgramManagerEntersApplicationProject.spec.ts,TowerVizion_ProgMGR
SiteSpecialistEnterInquiry.spec.ts,TowerVizion_Specialist
ApplicantEditsSubmittedApplication.spec.ts,TowerVizion_Applicant
```

Keep all test code, test data, fixtures, and test-specific configuration in this directory. Do not store credentials, access tokens, or other sensitive values in the repository; provide them through GitHub Actions secrets, repository variables, or environment variables.

## Local execution

The committed `.npmrc` only contains the registry configuration and does not contain a secret:

```ini
@ov-integrations:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
```

`NODE_AUTH_TOKEN` must contain a GitHub personal access token with the `read:packages` permission whenever `npm install` or `npm ci` is run. GitHub Actions provides this variable in CI. For local development, export it in your shell; do not replace the `${NODE_AUTH_TOKEN}` placeholder in the repository `.npmrc` with a real token.

From the repository root, install the dependencies and run the Playwright tests with the required application URL:

```bash
cd tests
export NODE_AUTH_TOKEN=<github-pat-with-read-packages>
export UI_TEST_WEB_URL=<application-url>
npm ci
npx playwright test
```

To run the tests in a specific browser, use the corresponding Playwright project configured by the shared framework:

```bash
npx playwright test --project=firefox
```

In GitHub Actions, the `run-module-tests.yml` workflow passes the selected browser and starts the reusable module-test workflow from `ov-integrations/module-test-actions`.
