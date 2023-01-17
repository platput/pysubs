#!/bin/bash

uvicorn pysubs.main:app --host="0.0.0.0" --port=8080 --log-level="info"
