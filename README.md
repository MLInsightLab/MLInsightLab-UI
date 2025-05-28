# MLInsightLab-UI

This repository contains the source code for the **ML Insight Lab UI Service**, which provides the web-based user interface for interacting with the ML Insight Lab Platform.

## Overview

The **UI Service** is the primary frontend for users of the ML Insight Lab. It is responsible for delivering a responsive, intuitive interface that allows users to interact with the platform.

The UI is served using **FastAPI**, which enables high-performance static file serving and integration with backend APIs.

## Build Status

[![UI Service CI](https://github.com/mlinsightlab/mlinsightlab-ui/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/mlinsightlab/mlinsightlab-ui/actions/workflows/docker-publish.yml)

This service is automatically built and published via GitHub Actions. You do **not** need to manually build or run this repository unless you are developing new UI features or fixing bugs.

## When to Use This Repository

You should pull and work on this repository **only** when:

- You are adding or updating frontend components or views
- You are modifying the UI behavior or user experience
- You are improving performance or fixing layout/styling issues
- You are extending API integrations or authentication workflows

For standard platform use, the UI service is built and deployed automatically.

---

We welcome UI/UX enhancements, accessibility improvements, and new feature contributions via issues or pull requests.
