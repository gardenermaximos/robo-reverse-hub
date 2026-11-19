#!/usr/bin/env bash
# gen_ts_types.sh — Generate TypeScript types from the OpenAPI spec.
# Requires: openapi-typescript (npm i -g openapi-typescript)
# Run after the backend is up at :8000

set -e
npx openapi-typescript http://127.0.0.1:8000/openapi.json \
    -o frontend/src/api/types.gen.ts
echo "Types written to frontend/src/api/types.gen.ts"
