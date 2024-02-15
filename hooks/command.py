#!/usr/bin/env python3

import base64
import http.client
import os
import re
import subprocess

proto = "https"
host = "github.com"

match = re.match("^{}://{}/(.*?)(?:.git)?$".format(re.escape(proto), re.escape(host)), os.environ["BUILDKITE_REPO"])
repo = match[1]

if match is None:
    print("Only HTTPS GitHub repository URLs are supported")
    exit(1)

process = subprocess.run(("git", "credential", "fill"), text=True, input="protocol={}\nhost={}\npath={}\n".format(proto, host, repo), capture_output=True, timeout=10)

if process.returncode != 0:
    print("Error fetching git credentials:", process.stderr)
    exit(1)

credentials = dict(line.split("=") for line in process.stdout.splitlines())

path = os.environ.get("BUILDKITE_PLUGIN_GITHUB_PIPELINE_UPLOAD_PATH", ".buildkite/pipeline.yml")
ref = os.environ.get("BUILDKITE_COMMIT")
if ref is None or ref == "HEAD":
    ref = os.environ.get("BUILDKITE_BRANCH", "HEAD")

headers = {
    "Host": "api.github.com",
    "User-Agent": "https://github.com/sj26/github-pipeline-upload-buildkite-plugin",
    "Authorization": "Bearer {}".format(credentials["password"]),
    "Accept": "application/vnd.github.v3.raw",
    "X-GitHub-Api-Version": "2022-11-28",
}

conn = http.client.HTTPSConnection("api.github.com")

conn.request("GET", "/repos/{}/contents/{}?ref={}".format(repo, path, ref), headers=headers)

response = conn.getresponse()

if response.status != 200:
    print("Error fetching {}:".format(path), response.status, response.reason)
    print(response.read())
    exit(1)

pipeline = response.read()

process = subprocess.run(("buildkite-agent", "pipeline", "upload"), input=pipeline)

if process.returncode != 0:
    print("Error uploading pipeline.")
    exit(1)
