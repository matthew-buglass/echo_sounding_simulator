#!/usr/bin/env bash

cp README.md docs/index.md
cp -r readme_imgs docs/readme_imgs
mkdocs build -d docs_out
