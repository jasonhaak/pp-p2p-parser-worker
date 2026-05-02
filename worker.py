# -*- coding: utf-8 -*-
"""
Cloudflare Python Worker entrypoint for the P2P statement parser.
"""
import json
import re
from urllib.parse import urlparse

from workers import Response
from workers import WorkerEntrypoint

from src.p2p_statement_parser import ParserInputError
from src.p2p_statement_parser import detect_provider_from_csv_text
from src.p2p_statement_parser import parse_csv_text
from src.provider_configs import PROVIDER_CONFIGS


AGGREGATES = {"transaction", "daily", "monthly"}
AUTO_PROVIDER = "auto"


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = urlparse(request.url)

        if url.path == "/parse":
            return await parse_request(request)

        return await self.env.ASSETS.fetch(request)


async def parse_request(request):
    if request.method == "OPTIONS":
        return Response("", status=204, headers=cors_headers())

    if request.method != "POST":
        return json_response({"error": "POST /parse is required"}, status=405)

    try:
        form_data = await read_form_data(request)
        provider = form_value(form_data.get("provider"), "auto")
        aggregate = form_value(form_data.get("aggregate"), "transaction")
        file_part = form_data.get("file")

        if provider != AUTO_PROVIDER and provider not in PROVIDER_CONFIGS:
            return json_response({"error": "Unsupported provider"}, status=400)
        if aggregate not in AGGREGATES:
            return json_response({"error": "Unsupported aggregate mode"}, status=400)
        if file_part is None:
            return json_response({"error": "CSV file is required"}, status=400)

        csv_text = await read_form_file(file_part)
        if not csv_text.strip():
            return json_response({"error": "CSV file is empty"}, status=400)

        detected_provider = detect_provider_from_csv_text(csv_text)
        selected_provider = detected_provider if provider == AUTO_PROVIDER else provider
        output_csv = parse_csv_text(csv_text=csv_text, provider=provider, aggregate=aggregate)
        if not output_csv:
            return json_response(
                {
                    "error": build_no_statement_message(selected_provider, detected_provider),
                    "detected_provider": detected_provider,
                },
                status=422,
            )

        filename = "portfolio_performance__{}.csv".format(safe_filename(selected_provider))
        headers = {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition": 'attachment; filename="{}"'.format(filename),
            **cors_headers(),
        }
        return Response(output_csv, headers=headers)
    except ParserInputError as exc:
        return json_response({"error": str(exc)}, status=400)
    except (KeyError, ValueError) as exc:
        return json_response({"error": "Could not parse the selected provider format: {}".format(exc)}, status=400)
    except Exception as exc:
        return json_response({"error": str(exc)}, status=500)


async def read_form_file(file_part):
    text_method = getattr(file_part, "text", None)
    if text_method:
        return await text_method()
    return str(file_part)


async def read_form_data(request):
    form_data_method = getattr(request, "formData", None)
    if form_data_method:
        return await form_data_method()

    form_data_method = getattr(request, "form_data", None)
    if form_data_method:
        return await form_data_method()

    content_type = get_header(request, "content-type")
    if "multipart/form-data" not in content_type:
        raise ValueError("multipart/form-data is required")

    text_method = getattr(request, "text", None)
    if not text_method:
        raise ValueError("Request body text reader is unavailable")

    body = await text_method()
    return parse_multipart_form(body, content_type)


def get_header(request, name):
    headers = getattr(request, "headers", None)
    if headers is None:
        return ""

    get_method = getattr(headers, "get", None)
    if get_method:
        value = get_method(name)
        return str(value or "")

    try:
        return str(headers[name] or "")
    except Exception:
        return ""


def parse_multipart_form(body, content_type):
    boundary_match = re.search(r'boundary="?([^";]+)"?', content_type)
    if not boundary_match:
        raise ValueError("multipart boundary is missing")

    boundary = "--" + boundary_match.group(1)
    fields = {}

    for part in body.split(boundary):
        if not part or part == "--" or part == "--\r\n":
            continue
        if part.startswith("--"):
            continue
        if part.startswith("\r\n"):
            part = part[2:]
        if "\r\n\r\n" not in part:
            continue

        raw_headers, value = part.split("\r\n\r\n", 1)
        if value.endswith("\r\n"):
            value = value[:-2]
        if value.endswith("--"):
            value = value[:-2]

        name_match = re.search(r'name="([^"]+)"', raw_headers)
        if name_match:
            fields[name_match.group(1)] = value

    return fields


def form_value(value, default):
    if value is None:
        return default
    value = str(value).strip()
    return value if value else default


def safe_filename(value):
    return "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in value)


def build_no_statement_message(selected_provider, detected_provider):
    message = "No supported Portfolio Performance statements were found for provider '{}'.".format(selected_provider)
    if detected_provider and detected_provider != selected_provider:
        message += " The uploaded CSV looks like provider '{}'; select that provider and try again.".format(
            detected_provider
        )
    else:
        message += " Check that this is an account-statement export and not a different CSV report."
    return message


def json_response(payload, status=200):
    return Response(
        json.dumps(payload),
        status=status,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            **cors_headers(),
        },
    )


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
