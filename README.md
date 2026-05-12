# pp-p2p-parser-ui

[![Release](https://img.shields.io/github/v/release/jasonhaak/pp-p2p-parser-ui)](https://github.com/jasonhaak/pp-p2p-parser-ui/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/jasonhaak/pp-p2p-parser-ui/ci.yml?branch=main&logo=github)](https://github.com/jasonhaak/pp-p2p-parser-ui/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/github/jasonhaak/pp-p2p/graph/badge.svg)](https://codecov.io/github/jasonhaak/cloudflare-outlook-calendar-worker)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-F38020?logo=cloudflare)](https://workers.cloudflare.com/)
[![Python](https://img.shields.io/badge/Python-Workers-306998?logo=python)](https://developers.cloudflare.com/workers/languages/python/)

A Cloudflare Worker, converting P2P account statement CSV exports into Portfolio Performance compatible CSV files. The Worker accepts a statement export, detects or uses the selected provider format, applies optional aggregation and returns a downloadable import file.

The project also keeps the original command line workflow for local batch conversion.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Supported Providers](#supported-providers)
- [How it Works](#how-it-works)
- [Aggregation Modes](#aggregation-modes)
- [Installation & Development](#installation--development)
- [Testing](#testing)
- [Endpoints](#endpoints)
- [Iframe Usage](#iframe-usage)
- [CLI Usage](#cli-usage)
- [Configuration](#configuration)
- [Author & Licence](#author--licence)

## Features

- **Cloudflare Worker UI**: Serves a lightweight upload interface and parser API from one Worker
- **CSV Provider Detection**: Detects supported formats from CSV headers and suggests the matching provider
- **Portfolio Performance Output**: Generates a CSV import file using Portfolio Performance compatible columns
- **Aggregation Modes**: Supports `transaction`, `daily`, and `monthly` aggregation
- **Multiple Language Formats**: Supports language-specific provider variants such as `mintos_en`, `mintos_de`, `estateguru_de` and `estateguru_en`
- **No Runtime Storage**: Uploaded files are read for conversion only and are not stored by the app
- **CLI Compatibility**: Keeps a local command line parser for existing workflows

## Quick Start

You will learn how to run the Worker locally, open the built-in UI, upload a CSV export and download a Portfolio Performance import file.

### 1. Prepare the Codebase

Clone or fork this repository:

```shell
git clone https://github.com/jasonhaak/pp-p2-parser-ui.git
cd pp-p2-parser-ui
```

### 2. Run Locally

Start the Cloudflare Worker development server:

```shell
npx wrangler@latest dev
```

Open the local UI:

```text
http://localhost:8787
```

### 3. Convert a CSV File

- Upload a CSV account statement export.
- Keep `Auto-Detect` selected or choose the provider manually.
- Choose an aggregation mode.
- Click **Convert** and save the generated CSV file.

### 4. Deploy to Cloudflare

Deploy the Worker:

```shell
npx wrangler@latest deploy
```

## Supported Providers

| Provider key | Format |
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

## How it Works

The browser sends the selected CSV file to `POST /parse` as multipart form data. The Worker reads the file, validates the selected provider format, parses supported booking rows, writes Portfolio Performance compatible CSV content, and returns it as a downloadable response.

The UI can detect the likely provider from the CSV header row. If the selected provider does not match the uploaded file, the error message explains which provider the file appears to use.

## Aggregation Modes

- `transaction`: Exports each supported booking as a separate row.
- `daily`: Summarizes bookings of the same type per day.
- `monthly`: Summarizes bookings of the same type per month and uses the last day of the month as the booking date.

Monthly aggregation can create booking dates later than the import date for the current month. Portfolio Performance may ignore future-dated rows.

## Installation & Development

### Worker Development

The Worker uses Cloudflare's built-in Python runtime SDK via the `disable_python_external_sdk` compatibility flag in `wrangler.toml`.

```shell
npx wrangler@latest dev
```

The static UI lives in `public/`. The Python Worker entrypoint is `worker.py`.

### Python Development

Create a virtual environment if you want to run the Python tests locally:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r dev-requirements.txt
```

## Testing

Run the Python test suite:

```shell
python3 -m unittest discover -s src/test -q
```

Check Python syntax:

```shell
python3 -m py_compile worker.py parse-account-statements.py src/*.py
```

Check frontend JavaScript syntax:

```shell
node --check public/app.js
```

## Endpoints

### `GET /`

Serves the static upload UI.

### `POST /parse`

Accepts multipart form data:

| Field | Description |
| --- | --- |
| `file` | CSV account statement export |
| `provider` | Provider key, or `auto` |
| `aggregate` | `transaction`, `daily`, or `monthly` |

Example:

```shell
curl -X POST http://localhost:8787/parse \
  -F "provider=auto" \
  -F "aggregate=transaction" \
  -F "file=@src/test/testdata/mintos.csv" \
  -o /tmp/portfolio_performance.csv
```

Successful responses return `text/csv` with a `Content-Disposition` download filename.

## Iframe Usage

The UI is designed to be embedded in another page. It automatically switches to embedded mode when loaded inside an iframe. You can also force embedded mode with:

```text
https://your-worker.example/?embedded=true
```

Recommended host CSS:

```css
iframe {
  width: 100%;
  min-height: 720px;
  border: 0;
  background: #F6F6F6;
  display: block;
}
```

## CLI Usage

The local CLI remains available:

```shell
./parse-account-statements.py --type mintos_en src/test/testdata/mintos.csv
```

Available aggregation modes:

```shell
./parse-account-statements.py --type mintos_en --aggregate daily src/test/testdata/mintos.csv
```

The CLI writes `portfolio_performance__<provider>.csv` next to the input file.

## Configuration

Provider parsing rules are bundled in `src/provider_configs.py` for Worker runtime use. YAML reference files are kept in `config/` using language-specific names where applicable, for example:

- `config/mintos_en.yml`
- `config/mintos_de.yml`
- `config/estateguru_de.yml`
- `config/estateguru_en.yml`

## Author & Licence

This project is not affiliated with Portfolio Performance or any P2P lending platform.

Original parser work comes from the PP-P2P-Parser project. This repository adapts it into a Cloudflare Worker UI.

Licensed under GPL-3.0. See [LICENSE](LICENSE).
