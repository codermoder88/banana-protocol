# Coding Challenge – Backend 2025

## Application Requirements

Imagine that we are building a service that receives weather data from various sensors that report metrics such as temperature, humidity, wind speed, etc.  
Your task in this coding challenge is to build an application that solves part of this problem:

- The application can receive new metric values as the weather changes around the sensor via an API call.
- The application must allow querying sensor data.  
  A query should define:
  - One or more (or all sensors) to include in results.
  - The metrics (e.g., temperature and humidity); the application should return the average value for these metrics.
  - The statistic for the metric: **min**, **max**, **sum**, or **average**.
  - A **date range** (between one day and a month). If not specified, the latest data should be queried.
  - **Example query:** “Give me the average temperature and humidity for sensor 1 in the last week.”

---

## Technical Requirements

- The application should be a **REST API** (no UI needed).
- Programming language: preferably **Java**, **JavaScript/TypeScript**, or **Python**.
- The application data must be **persisted in a database/storage**.
- Include **input validation** and **exception handling** where necessary.

---

## Other Notes

- Treat this as a **proof of concept** — not everything must be perfect.  
  If some parts are incomplete, **explain what’s missing**.
- **Documentation** is nice to have but not required.
- Implement **unit/integration tests** as you find necessary. Full coverage is not expected.
- Include clear **instructions** in your **README** on how to run the project.
