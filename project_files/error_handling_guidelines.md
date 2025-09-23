# Error Handling Guidelines

## Introduction

Effective error handling is crucial for maintaining system reliability, improving developer productivity, and delivering a seamless user experience. This document outlines comprehensive guidelines for classifying, diagnosing, and resolving errors within our systems. By following these standards, we ensure consistent, efficient, and transparent handling of all error scenarios.

---

## Error Classification Categories

Errors should be classified into the following categories to streamline diagnosis and resolution:

- **User-Facing Errors:** Errors that impact the end-user experience and require clear, user-friendly messaging.
- **Internal Errors:** System or infrastructure errors not directly exposed to users but critical for operational awareness.
- **Transient Errors:** Temporary failures, such as network timeouts or resource contention, which may succeed on retry.
- **Permanent Errors:** Failures that require intervention or code changes to resolve.
- **Validation Errors:** Input or configuration issues that prevent normal operation.
- **Timeouts and Lock Contention:** Specific errors caused by resource delays or blocking, requiring distinct handling.
- **Performance-Related Errors:** Failures triggered by exceeding performance thresholds, e.g., >5% allocation failures.

---

## Hypothesis Rules

When investigating errors, hypotheses should be:

1. **Ranked by Likelihood:** Prioritize hypotheses based on system knowledge, recent changes, and error patterns.
2. **Multiple Hypotheses:** Generate at least 2-3 plausible causes before proceeding.
3. **Quick Checks First:** Use fast, low-impact tests (logs, metrics, quick repro) to validate or discard hypotheses before deeper investigation.

---

## Minimal Repro Checklist

To efficiently diagnose errors, always create a minimal reproducible example:

1. **Step-by-Step Instructions:** Document precise steps to reproduce the issue.
2. **Minimal Dataset:** Use the smallest possible data subset or configuration to trigger the error.
3. **Environment Details:** Include relevant environment information (OS, versions, configurations).
4. **Isolation:** Eliminate unrelated variables to isolate the root cause.
5. **Repeatability:** Ensure the error consistently reproduces under these conditions.

---

## Regression Testing Rules

Regression tests prevent reintroduction of resolved errors and must adhere to:

- **Naming Conventions:** Tests should clearly indicate the bug or feature fixed (e.g., `test_fix_timeout_issue`).
- **Coverage:** Every fix must include at least one regression test.
- **Automated Execution:** Tests should run automatically in CI/CD pipelines.
- **Documentation:** Include a brief description of the regression scenario and expected behavior.

---

## Debugging Templates

Follow this structured approach for debugging and documenting errors:

1. **Classification:** Identify error category (e.g., transient, validation, internal).
2. **Hypotheses:** List ranked potential causes.
3. **Repro:** Provide minimal reproduction steps and environment.
4. **Fix:** Describe the resolution or workaround.
5. **Regression:** Detail regression tests added.

Always include an **“Explain Like I’m New”** section that clarifies the issue and fix in simple terms for onboarding and knowledge sharing.

### Examples

**Good Debugging Response:**

- Classification: Transient network timeout.
- Hypotheses:
  1. Network congestion causing dropped packets.
  2. Misconfigured timeout settings.
- Repro: Using test script `network_test.sh` with minimal data set, error reproducible 90% of attempts.
- Fix: Increased timeout from 5s to 15s, added retry logic with exponential backoff.
- Regression: Added `test_network_timeout_retry` to CI.
- Explain Like I’m New: The system was timing out because it waited too little for responses. By waiting longer and retrying, it now handles slow networks better.

**Bad Debugging Response:**

- Error happened, fixed it by changing timeout.
- No hypotheses or repro steps.
- No tests added.
- No explanation.

---

## Logging & Observability

- Use **structured JSON logs** for all errors to enable easy parsing and correlation.
- Include **correlation IDs** to trace requests across services.
- Maintain **audit logs** for critical error events and user-facing incidents.
- Log enough context (timestamps, user IDs, request parameters) without exposing sensitive data.
- Use standardized error codes and messages to facilitate automated monitoring and alerting.

---

## Internal vs User-Facing Errors

- **Internal Errors:** Should include full diagnostic details for developers but never expose sensitive schema or stack traces to users.
- **User-Facing Errors:** Must be redacted of technical details, using clear, actionable language.
- Implement a redaction schema to automatically sanitize error messages before user display.

---

## Retry & Recovery

- Implement **automatic retries** for transient errors with **exponential backoff and jitter** to avoid thundering herd issues.
- Define retry limits and fallback mechanisms to prevent infinite loops.
- For recoverable errors, provide clear status indicators and recovery paths.
- Log retry attempts and outcomes for monitoring.

---

## Performance & Error Impact

- Separate handling for **timeouts and lock contention** errors to avoid masking underlying issues.
- Define thresholds for error tolerance; for example, fail processes if **more than 5% of allocations fail**.
- Monitor performance metrics continuously and trigger alerts when error impact exceeds thresholds.
- Use circuit breakers or rate limiters to protect system stability under error conditions.

---

By adhering to these guidelines, we foster robust error handling practices that improve system resilience, developer efficiency, and user satisfaction.
