# GitHub Pipeline Upload

What if I told you that you don't need to clone your whole git repository to upload a single pipeline file?

If you're using Buildkite with an HTTPS GitHub repository then you can! Just swap your pipeline upload step to:

```yaml
steps:
  - label: ":pipeline:"
    plugins:
    - sj26/github-pipeline-upload: ~
```

YMMV.
