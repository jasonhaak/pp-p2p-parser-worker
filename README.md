# pp-p2p-parser-ui
[![Release](https://img.shields.io/github/v/release/jasonhaak/pp-p2p-parser-ui)](https://github.com/jasonhaak/pp-p2p-parser-ui/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/jasonhaak/pp-p2p-parser-ui/ci.yml?branch=main&logo=github)](https://github.com/jasonhaak/pp-p2p-parser-ui/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/github/jasonhaak/pp-p2p-parser-ui/graph/badge.svg)](https://codecov.io/github/jasonhaak/pp-p2p-parser-ui)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-F38020?logo=cloudflare)](https://workers.cloudflare.com/)

A Cloudflare Worker for converting an exported P2P account statement `.csv` into a Portfolio Performance compatible `.csv` file. The Worker accepts a statement export, detects or uses the selected provider format, applies optional aggregation and returns a downloadable import file for Portfolio Performance.

## Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
  - [Supported Providers](#supported-providers)
  - [Aggregation Mode](#aggregation-mode)
  - [Output Language](#output-language)
- [How it Works](#how-it-works)
- [Installation & Development](#installation--development)
- [Testing](#testing)
- [Endpoints](#endpoints)
- [iFrame Usage](#iframe-usage)
- [CLI Usage](#cli-usage)
- [Author & Licence](#author--licence)

## Features
- **Conversion**: Upload a `.csv` export and get a Portfolio Performance compatible `.csv` file in response
- **Multiple Provider and Language Support**: Supports multiple P2P lending platforms with language-specific format variants
- **Auto-Detection**: Detects the likely provider format from the `.csv` header row when `Auto-Detect` is selected
- **Aggregation Modes**: Supports different aggregation modes for bookings of the same type on the same day or month, in addition to exporting each transaction separately
- **CLI Compatibility**: Keeps a Python local command line parser for existing workflows

## Quick Start
You will learn how to deploy the worker to Cloudflare, open the built-in UI, upload a `.csv` export and download a Portfolio Performance-ready import file.

### 1. Prepare the Codebase
Cloudflare always requires a code source (repository or ZIP) to deploy a Worker. Choose one of the following:
- **Git (recommended)**: Fork this repository into your own GitHub/GitLab account.
- **ZIP (manual upload)**: Download the code as a ZIP file and prepare it for upload.

### 2. Add a Worker in Cloudflare
- Log in to the [Cloudflare Dashboard](https://dash.cloudflare.com/).
- Navigate to **Workers & Pages -> Workers** and create a new Worker with the name `cloudflare-outlook-calendar-worker`.

### 3. Deploy
- **Cloudflare Git integration (recommended)**: Connect your forked repository directly to your GitHub/GitLab account in the Cloudflare Dashboard. Cloudflare will build and deploy automatically. Additional information about the Git integration for Cloudflare Workers can be found in the [Cloudflare documentation](https://developers.cloudflare.com/workers/ci-cd/builds/).
- **ZIP (manual upload)**: Upload your prepared ZIP file using the Dashboard’s editor or deployment UI.
- **Wrangler**: Deploy from your local checkout with `npm run deploy`.
- **CI pipeline**: If you want to have control over the CI checks and deployment, you can set up your own pipeline that runs the tests and deploys to Cloudflare. You can use the same CI configuration as this repository, which is available in `.github/workflows/ci.yml`. Make sure to update the deployment step with your own Cloudflare API credentials and Worker name. Additional information on setting up CI/CD pipelines for Cloudflare Workers can be found in the [Cloudflare documentation](https://developers.cloudflare.com/workers/ci-cd/external-cicd/).

> **Important:** When using Cloudflare Git integration, go to **Settings -> Build -> Branch Control** in your Worker project. Make sure to **deactivate** (uncheck) the option for enabling builds for non-production branches. If this setting is active, any push to your `develop` (or other non-production) branch will trigger a deployment to your Worker, which may not be desired for production stability.

### 4. Open the UI and use the Service
Open:

```text
https://<your-worker>.<your-subdomain>.workers.dev/
```

Upload a `.csv` export from one of the supported providers, select the provider or keep `Auto-Detect`, choose the Portfolio Performance language and aggregation mode, then click *Convert* to download a compatible `.csv` file.

## Configuration
### Supported Providers
| Provider Key | Format |
| --- | --- |
| `bondora` | Bondora account statement |
| `bondora_go_grow` | Bondora Go & Grow account statement |
| `debitumnetwork` | Debitum Network account statement |
| `estateguru_de` | EstateGuru German export |
| `estateguru_de_legacy` | EstateGuru older German export |
| `estateguru_en` | EstateGuru English export |
| `lande` | Lande account statement |
| `mintos_de` | Mintos German export |
| `mintos_en` | Mintos English export |
| `robocash` | Robocash account statement |
| `swaper` | Swaper account statement |
| `viainvest` | Viainvest account statement |

### Aggregation Mode
| Mode | Behavior | Best Use |
| --- | --- | --- |
| `transaction` | Exports each supported booking as a separate row. | Default and recommended mode when you want a detailed import history. |
| `daily` | Groups bookings with the same date, transaction type and currency into one row per day. | Reducing many small transactions while keeping daily totals. |
| `monthly` | Groups bookings with the same transaction type and currency into one row per month, dated on the last day of the month. | Compact long-term imports. Be careful with the current month because Portfolio Performance may ignore future-dated rows. |

Monthly aggregation can create booking dates later than the import date for the current month. Portfolio Performance may ignore future-dated rows.

### Output Language
- `de`: German column names and transaction types. This is the default for backwards compatibility.
- `en`: English column names and transaction types.

## How it Works
### Provider Detection
P2P platforms export account statements in different CSV formats. Column names, date formats, transaction descriptions and language variants differ between providers. When the user selects a file, the browser reads the CSV header row and tries to detect the provider locally by comparing the uploaded headers with the required columns from the supported provider configurations.

If detection succeeds, the provider dropdown is updated automatically. If detection fails, the UI keeps `Auto-Detect` selected and shows a warning so the user can choose a provider manually.

If a provider is selected manually, the Worker verifies that the required columns exist before parsing. If the headers look like another provider, the error message names the likely match.

### Aggregation
This Worker supports three aggregation modes:

| Mode | Behavior |
| --- | --- |
| `transaction` | Each supported input row is converted directly into one Portfolio Performance output row. Keeps the original booking date, value, currency, mapped transaction type and generated note. |
| `daily` | Supported rows are grouped by booking date and mapped transaction type. Values in each group are summed. The output note is `Tageszusammenfassung` in German output and `Daily summary` in English output. The first currency seen for the group is used. |
| `monthly` | Supported rows are grouped by month and mapped transaction type. Values in each group are summed and the output date is set to the last day of that month. The output note is `Monatszusammenfassung` in German output and `Monthly summary` in English output. Monthly rows for the current month may be dated in the future and can be ignored by Portfolio Performance. |

### Portfolio Performance Output

At the final CSV writing step, the selected output language controls the exported column headers, transaction type labels and generated aggregation notes. Provider detection and parsing are independent from the output language.

| Output Language | Header | Transaction Types |
| --- | --- | --- |
| `de` | `Datum,Wert,Buchungswährung,Typ,Notiz` | `Einlage`, `Entnahme`, `Zinsen`, `Gebühren` |
| `en` | `Date,Value,Transaction Currency,Type,Note` | `Deposit`, `Withdrawal`, `Interest`, `Fees` |

### Parsing & Conversion
When the user clicks **Convert**, the browser sends the CSV file and selected options to `POST /parse`. The Worker validates the provider, aggregation mode, output language and CSV content.

Each supported row is mapped to a Portfolio Performance account transaction category by matching the provider-specific transaction description against configured regular expressions. Unsupported or intentionally ignored transaction descriptions are skipped. Input values with comma or dot decimal separators, including common thousands-separator formats, are normalized before conversion. The provider currency column is used when available. Providers without a currency column default to `EUR`.

Finally, the Worker returns a downloadable Portfolio Performance CSV file. If an error occurs, it is returned as JSON and shown in the UI as a red status message.

## Installation & Development
1. **Clone the Repository**
   ```bash
   git clone https://github.com/jasonhaak/pp-p2p-parser-ui.git
   cd pp-p2p-parser-ui
   ```

2. **Install Dependencies**
   There are no project-local npm dependencies and no required Python runtime dependencies for the Worker. The Worker uses Cloudflare's built-in Python runtime SDK via the `disable_python_external_sdk` compatibility flag in `wrangler.toml`.

   For local development you need:
   - Node.js with `npx` to run Wrangler
   - Python 3 to run tests and local parser commands

3. **Run the Worker Locally**
   ```bash
   npx wrangler dev
   ```
   
   Open the local UI at:
   ```text
   http://localhost:8787
   ```
   
### Provider Configuration
The provider configuration files are located in `config`. Each provider has a `.yml` file defining the expected `.csv` format, column mappings and parsing rules. You can add new providers by creating a new configuration file following the existing examples.

The `.yml` provider configuration is converted in the CI pipeline with the help of `tools/generate_provider_configs.py` into the `src/provider_configs.py` module. This module is imported by the Worker to access the provider definitions for parsing and conversion.

## Testing
This project uses Python's built-in `unittest` for unit tests. Test data for each provider is located in `test/testdata`.  Additionally, the CI pipeline runs syntax checks for converting and validating the configuration files for each provider, Worker bundle validation, Python and JavaScript code as well as code coverage.

Run the suite locally to test core parsing and conversion logic:

```shell
python3 -m unittest discover -s test
```

Check Python syntax for all source files:

```shell
python3 -m py_compile src/*.py tools/*.py
```

Check frontend JavaScript syntax for testing the UI:

```shell
node --check public/app.js
```

## Endpoints
| Route | Description |
| --- | --- |
| `GET /` | Serves the static upload UI |
| `POST /parse` | Accepts a `.csv` export and returns a Portfolio Performance compatible `.csv` file in response |

### `/parse` Query Parameters
| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `file` | Yes | N/A | The `.csv` file to be converted, sent as multipart form data |
| `provider` | No | `auto` | The provider format to use for parsing. If `auto` is selected, the Worker will attempt to detect the provider format from the header row of the uploaded `.csv` file. |
| `aggregate` | No | `transaction` | The aggregation mode to apply to the output file. |
| `output_language` | No | `de` | The language to use for column names and transaction types in the output file. |

### Example
Example `curl` request for the API endpoint:

```shell
curl -X POST http://localhost:8787/parse \
  -F "file=@test/testdata/mintos.csv" \
  -F "provider=auto" \
  -F "aggregate=transaction" \
  -F "output_language=en" \
  -o /tmp/portfolio_performance.csv
```

Successful responses return `text/csv` with a `Content-Disposition` download filename.

## iFrame Usage
The UI is designed to be embedded in another page. It automatically switches to embedded mode when loaded inside an iframe. You can also force embedded mode with `/embed` or `/?embed=1`.

Recommended iFrame embedding:

```css
iframe {
  width: 100%;
  min-height: 720px;
  border: 0;
  background: #F6F6F6;
  display: block;
}
```

The embed view removes the footer, outer spacing, shadow and rounded outer frame.

The UI response also sends:

```text
Content-Security-Policy: frame-ancestors *
```

Adjust this header before production use if you only want specific domains to embed the UI.

## CLI Usage
The local CLI remains available. It accepts the same provider, aggregation and output language options as the Worker. The CLI writes the converted file next to the input file with the name `portfolio_performance__<provider>__<language>.csv`:

```shell
python3 -m src.cli --type mintos_en test/testdata/mintos.csv
```

Available aggregation modes:

```shell
python3 -m src.cli --type mintos_en --aggregate daily test/testdata/mintos.csv
```

Available output languages:

```shell
python3 -m src.cli --type mintos_en --output-language en test/testdata/mintos.csv
```

## Author & Licence
This project is maintained by Jason Haak and is licensed under the GPL-3.0 licence.

The original parser work comes from ChrisRBe's [PP-P2P-Parser](https://github.com/ChrisRBe/PP-P2P-Parser) repository. This project adapts that parser into a Cloudflare Worker UI.

This project is not affiliated with Portfolio Performance or any P2P lending platform.