# test-automation-framework
A data-driven REST API test automation framework with pytest, Docker, CI, and Allure reporting deployed to GitHub Pages.

In typical unit tests, test data and test logic are tightly coupled. After a while it becomes hard to tell what is actually being tested. This framework separates the two: the test logic stays generic, while parameters and expected results are defined in separate YAML test cases. Tests can be added or changed by editing data, without editing the test code. 

A bundled mock server serves as a demonstration backend for REST API tests.



## Quick start:

```bash
# 1. start the mock server
uv run uvicorn mock_server.main:app --host 127.0.0.1 --port 8787

# 2. run all tests
uv run run.py
```


## Features

- **Layered architecture** — `conf` (config), `common` (utilities), `base` (request/assertion components), `testcase` (test data); test logic is fully separated from test cases
- **YAML-based test cases** — add or modify cases by editing YAML, no code changes needed
- **Data-driven parametrization** — one YAML file generates multiple independent test cases
- **Unified request handling** — supports multiple HTTP methods and parameter types through a single interface, with runtime injection of variables such as tokens via reflection
- **Response extraction & chaining** — extract values from one response and pass them to subsequent requests for scenario testing
- **Session-scoped login** — authentication handled once per session via a dedicated fixture
- **Async polling** — retry mechanism for long-running jobs
- **Database assertion** — validate test results against MySQL, ensuring data is correctly persisted
- **xfail / skip handling** — for known limitations and environment-dependent tests
- **Dockerized mock server** — self-contained backend, no external dependencies
- **CI integration** — tests run automatically on push; Allure report generated and deployed to GitHub Pages
- **Slack notifications** — test results pushed to Slack after a run

[View the latest Allure report](https://qianlint.github.io/test-automation-framework/)
<img width="1456" height="817" alt="Allure_example" src="https://github.com/user-attachments/assets/6120938c-7d77-48b9-85c9-d27175e50dfd" />


