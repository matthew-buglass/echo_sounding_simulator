#!/usr/bin/env bash

cp README.md docs_source/index.md
cp -r readme_imgs docs_source
mkdocs build --clean
