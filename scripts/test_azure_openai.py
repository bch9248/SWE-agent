#!/usr/bin/env python3
"""
Simple script to test Azure OpenAI connectivity.

Usage:
  python scripts/test_azure_openai.py [--endpoint ENDPOINT] [--key KEY] [--deployment DEPLOYMENT]

Env vars:
  AZURE_OPENAI_ENDPOINT  e.g. https://<resource-name>.openai.azure.com
  AZURE_OPENAI_KEY       the API key
  AZURE_OPENAI_DEPLOYMENT  the deployment name (model deployment)

If you don't have `requests` installed, run:
  pip install requests
"""

import os
import sys
import argparse
import json

try:
    import requests
except Exception:
    print("The 'requests' library is required. Install with: pip install requests")
    sys.exit(2)


def load_env_file(path):
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)


def main():
    parser = argparse.ArgumentParser(description="Test Azure OpenAI API connectivity")
    parser.add_argument('--endpoint', help='Azure OpenAI endpoint (https://<name>.openai.azure.com)')
    parser.add_argument('--key', help='Azure OpenAI API key')
    parser.add_argument('--deployment', help='Deployment name (model deployment)')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    # try to load a local .env if present (project root)
    load_env_file('.env')

    endpoint = args.endpoint or os.environ.get('AZURE_OPENAI_ENDPOINT') or os.environ.get('OPENAI_API_BASE')
    key = args.key or os.environ.get('AZURE_OPENAI_KEY') or os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_KEY')
    deployment = args.deployment or os.environ.get('AZURE_OPENAI_DEPLOYMENT') or os.environ.get('OPENAI_DEPLOYMENT')

    if not endpoint or not key or not deployment:
        print("Missing configuration. Provide --endpoint, --key, and --deployment or set env vars:")
        print("  AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT")
        sys.exit(2)

    # Build URL for chat completions (Azure OpenAI)
    url = endpoint.rstrip('/') + f"/openai/deployments/{deployment}/chat/completions?api-version=2023-05-15"
    headers = {
        'api-key': key,
        'Content-Type': 'application/json'
    }

    body = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 7 multiplied by 8?"}
        ],
        "max_tokens": 512,
        "temperature": 0
    }

    if args.verbose:
        print('POST', url)
        print('Headers:', {k: ('<redacted>' if k.lower() == 'api-key' else v) for k, v in headers.items()})
        print('Body:', json.dumps(body))

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
    except requests.exceptions.RequestException as e:
        print('Request failed:', str(e))
        sys.exit(1)

    print('HTTP status:', resp.status_code)
    try:
        j = resp.json()
    except ValueError:
        print('Non-JSON response:')
        print(resp.text)
        sys.exit(1)

    # Optionally show full JSON when verbose
    if args.verbose:
        print('Full JSON response:')
        print(json.dumps(j, indent=2))

    # Try to extract assistant content from common Azure/OpenAI chat response shapes
    assistant_text = None
    try:
        # Standard chat completion shape: choices -> message -> content
        if isinstance(j, dict) and 'choices' in j and len(j['choices']) > 0:
            choice = j['choices'][0]
            if isinstance(choice, dict):
                # new-style: choice['message']['content']
                msg = choice.get('message')
                if isinstance(msg, dict) and 'content' in msg:
                    assistant_text = msg.get('content')
                # fallback older style: choice['text']
                if assistant_text is None:
                    assistant_text = choice.get('text')

        # Another possible location: directly at 'message' key
        if assistant_text is None and isinstance(j, dict):
            if 'message' in j and isinstance(j['message'], dict):
                assistant_text = j['message'].get('content')

    except Exception:
        assistant_text = None

    if assistant_text:
        print('\n=== Model response ===')
        # Print the assistant reply cleanly
        if isinstance(assistant_text, list):
            # sometimes content can be a list of chunks
            for part in assistant_text:
                print(part)
        else:
            print(assistant_text)
        print('=== End ===\n')
        if resp.status_code == 200:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        # No assistant text found — fall back to printing the JSON for inspection
        print('No assistant message found in response; full response below:')
        print(json.dumps(j, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
