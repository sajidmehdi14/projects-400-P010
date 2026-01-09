---
name: fastapi-code-reviewer
description: Comprehensive FastAPI code review tool that analyzes Python FastAPI applications for bugs, security vulnerabilities, performance issues, and design problems. Use this skill when users request code review, security audit, performance analysis, or quality assessment of FastAPI code. Triggers include requests like "review my FastAPI code", "check for security issues", "analyze performance", "audit this endpoint", or when examining .py files containing FastAPI imports, route decorators (@app.get, @app.post), or FastAPI application patterns.
---

# FastAPI Code Reviewer

Conduct comprehensive code reviews of FastAPI applications, identifying bugs, security vulnerabilities, performance issues, and design problems with severity-based reporting.

## Review Process

### 1. Determine Scope

Analyze the provided code to determine review scope:

**Single file/endpoint:**
- Focus on route handler logic
- Check dependencies and middleware used
- Review data validation and error handling

**Full application:**
- Examine project structure and organization
- Review all route handlers and dependencies
- Analyze configuration and lifecycle management
- Check requirements.txt/pyproject.toml for dependency issues

### 2. Execute Category Reviews

Review code systematically across all four categories (detailed below):
1. Bugs
2. Security Issues
3. Performance Risks
4. Design Problems

### 3. Analyze Dependencies

When reviewing full applications or when requirements files are present:
- Check for outdated FastAPI version
- Identify deprecated dependencies
- Look for known security vulnerabilities in packages
- Verify compatibility between dependency versions

### 4. Generate Report

Produce severity-based output following the Output Format template below.

## Review Categories

### Bugs

Look for functional errors and common mistakes:

**Dependency Injection Issues:**
- Incorrect dependency function signatures
- Missing async/await in async dependencies
- Circular dependencies
- Dependencies with side effects

**Request/Response Handling:**
- Incorrect Pydantic model usage
- Missing or incorrect response_model declarations
- Type annotation errors
- Query/path parameter validation issues

**Async/Await Problems:**
- Mixing sync/async incorrectly
- Blocking I/O in async functions
- Missing await keywords
- Incorrect use of async context managers

**Lifecycle Issues:**
- Improper startup/shutdown event handling
- Resource leaks (unclosed connections, files)
- Background task errors

**Common Pitfalls:**
- Mutable default arguments in route handlers
- Global state mutations
- Incorrect exception handling
- Missing error responses

### Security Issues

Identify vulnerabilities and security weaknesses:

**Authentication & Authorization:**
- Missing authentication on sensitive endpoints
- Weak or missing API key validation
- Insecure JWT implementation (weak secrets, no expiration)
- Missing authorization checks
- Hardcoded credentials

**Input Validation:**
- SQL injection vulnerabilities (raw queries)
- NoSQL injection risks
- Command injection (os.system, subprocess without sanitization)
- Path traversal vulnerabilities
- Insufficient input validation beyond Pydantic

**Data Exposure:**
- Sensitive data in responses (passwords, tokens, internal IDs)
- Excessive data exposure (returning full models when partial needed)
- Logs containing sensitive information
- Verbose error messages exposing internals

**CORS & Headers:**
- Overly permissive CORS settings (allow_origins=["*"])
- Missing security headers
- Insecure cookie settings (missing secure, httponly, samesite)

**Dependencies:**
- Known CVEs in requirements
- Outdated security-critical packages
- Unnecessary dependencies increasing attack surface

**Other:**
- Missing rate limiting on sensitive endpoints
- Insufficient HTTPS enforcement
- Unvalidated redirects
- Missing CSRF protection where needed

### Performance Risks

Identify bottlenecks and optimization opportunities:

**Database Issues:**
- N+1 query problems
- Missing database connection pooling
- Lack of query optimization
- Missing indexes (inferred from query patterns)
- Synchronous database calls in async endpoints

**Blocking Operations:**
- Synchronous I/O in async routes
- CPU-intensive operations blocking event loop
- Missing background tasks for long operations
- File I/O without async alternatives

**Resource Management:**
- Unbounded response sizes
- Missing pagination on list endpoints
- Inefficient data serialization
- Memory leaks from unclosed resources

**API Design:**
- Overfetching data in responses
- Missing caching opportunities
- Inefficient middleware stacking
- Redundant validation or processing

**Concurrency:**
- Missing async benefits (using sync when async available)
- Thread-unsafe global state
- Improper use of connection pools

### Design Problems

Identify architectural and maintainability issues:

**Code Organization:**
- Poor separation of concerns
- Business logic in route handlers
- Missing service/repository layers
- Inconsistent project structure

**API Design:**
- Inconsistent endpoint naming
- Poor HTTP method usage (GET with side effects)
- Missing or incorrect status codes
- Inconsistent response formats
- Poor error response structure

**Dependencies & Configuration:**
- Overuse of global state
- Hardcoded configuration values
- Missing environment variable usage
- Poor dependency injection structure

**Data Models:**
- Mixing domain models with API models
- Missing response models
- Overly complex Pydantic models
- Poor validation structure

**Error Handling:**
- Inconsistent exception handling
- Missing custom exception handlers
- Poor error message structure
- Insufficient error context

**Testing Considerations:**
- Code structure difficult to test
- Missing dependency abstractions for testing
- Tight coupling preventing mocking

**Documentation:**
- Missing or incomplete docstrings
- Poor API documentation
- Missing OpenAPI customization
- Unclear endpoint purposes

## Dependency Analysis

When reviewing dependencies (requirements.txt, pyproject.toml):

1. **Version Check:**
   - Identify outdated packages
   - Check for deprecated versions
   - Verify FastAPI and Pydantic compatibility

2. **Security Scan:**
   - Note any packages with known CVEs
   - Identify unmaintained dependencies
   - Check for security-critical updates

3. **Compatibility:**
   - Verify Python version compatibility
   - Check for conflicting dependency versions
   - Identify deprecated packages

## Output Format

Structure review findings using this template:

```markdown
# FastAPI Code Review Report

## Executive Summary
[Brief overview: X critical, Y high, Z medium, W low severity issues found]

## Critical Issues
[Issues requiring immediate attention]

### [Category]: [Issue Title]
**Severity:** Critical
**Location:** `file.py:line_number` or `module_name`
**Description:** [Detailed explanation of the issue]
**Impact:** [Security risk, data loss risk, etc.]
**Recommendation:** [Specific fix with code example if applicable]

## High Severity Issues
[Important issues that should be addressed soon]

### [Category]: [Issue Title]
**Severity:** High
**Location:** `file.py:line_number`
**Description:** [Explanation]
**Impact:** [Performance degradation, maintainability issues, etc.]
**Recommendation:** [Fix suggestion]

## Medium Severity Issues
[Issues that should be addressed but aren't urgent]

[Brief list format acceptable for medium severity]
- [Issue summary with location]

## Low Severity Issues
[Minor improvements and best practices]

[Concise list format]
- [Issue summary]

## Positive Observations
[Highlight good patterns and practices found]

## Dependencies
[If applicable]
- Outdated: [package==version] → [latest_version]
- Security concerns: [package with CVE details]
- Recommendations: [upgrade suggestions]

## Summary Metrics
- Total Issues: [count]
- By Severity: Critical (X), High (Y), Medium (Z), Low (W)
- By Category: Bugs (X), Security (Y), Performance (Z), Design (W)
```

## Severity Classification

Use these guidelines to assign severity levels:

**Critical:**
- Security vulnerabilities allowing unauthorized access or data exposure
- Bugs causing data loss or corruption
- Issues causing application crashes or downtime
- Known CVEs in dependencies (CVSS 9.0+)

**High:**
- Security issues with moderate risk (auth weaknesses, injection possibilities)
- Significant performance bottlenecks
- Bugs affecting core functionality
- Major design flaws impacting maintainability
- Known CVEs (CVSS 7.0-8.9)

**Medium:**
- Security hardening opportunities
- Performance optimization opportunities
- Minor functional bugs
- Design improvements for better maintainability
- Outdated dependencies without known CVEs

**Low:**
- Code style inconsistencies
- Minor optimization opportunities
- Documentation improvements
- Best practice violations without immediate impact
- Refactoring suggestions

## Usage Examples

**Single endpoint review:**
```
User: "Review this FastAPI endpoint for security issues"
```

**Full application review:**
```
User: "Audit my FastAPI application for bugs and performance problems"
```

**Focused review:**
```
User: "Check this route handler for design issues"
```

**Dependency check:**
```
User: "Review my requirements.txt for security vulnerabilities"
```
