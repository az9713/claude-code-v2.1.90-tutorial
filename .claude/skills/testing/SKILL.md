---
name: testing
description: Testing patterns, strategies, and best practices for comprehensive test coverage.
triggers:
  - test
  - tests
  - testing
  - coverage
  - unit test
  - integration test
---
# Testing Skill

## Overview

This skill defines testing patterns, strategies, and best practices for achieving comprehensive test coverage across the project.

## Test Types

| Type | Purpose | Location | Speed |
|------|---------|----------|-------|
| Unit | Test isolated functions | `tests/unit/` | Fast |
| Integration | Test component interactions | `tests/integration/` | Medium |
| E2E | Test full user flows | `tests/e2e/` | Slow |

## Directory Structure

```
tests/
├── unit/
│   ├── utils/
│   │   └── helpers.test.js
│   └── services/
│       └── userService.test.js
├── integration/
│   ├── api/
│   │   └── userRoutes.test.js
│   └── database/
│       └── userRepository.test.js
├── e2e/
│   └── userFlow.test.js
├── fixtures/
│   └── testData.js
├── helpers/
│   └── testUtils.js
└── run.js
```

## Test File Naming

```
// Unit tests
[module].test.js
[module].spec.js

// Integration tests
[feature].integration.test.js

// E2E tests
[flow].e2e.test.js
```

## Writing Tests

### Basic Test Structure

```javascript
const { functionToTest } = require('../../app/module');

describe('ModuleName', () => {
  describe('functionToTest', () => {
    // Setup
    beforeEach(() => {
      // Reset state before each test
    });

    afterEach(() => {
      // Cleanup after each test
    });

    // Happy path tests
    describe('when given valid input', () => {
      test('returns expected result', () => {
        const result = functionToTest('valid');
        expect(result).toBe('expected');
      });
    });

    // Edge cases
    describe('edge cases', () => {
      test('handles empty input', () => {
        expect(functionToTest('')).toBe('default');
      });

      test('handles null input', () => {
        expect(functionToTest(null)).toBeNull();
      });
    });

    // Error cases
    describe('error handling', () => {
      test('throws on invalid input', () => {
        expect(() => functionToTest(undefined)).toThrow();
      });
    });
  });
});
```

### AAA Pattern

```javascript
test('calculateTotal returns correct sum with discount', () => {
  // Arrange - Setup test data
  const items = [{ price: 100 }, { price: 50 }];
  const discount = 0.1;

  // Act - Execute the code
  const result = calculateTotal(items, discount);

  // Assert - Verify the result
  expect(result).toBe(135); // (100 + 50) * 0.9
});
```

## Common Assertions

```javascript
// Equality
expect(value).toBe(expected);           // Strict equality
expect(value).toEqual(expected);        // Deep equality
expect(value).not.toBe(unexpected);     // Negation

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeLessThan(5);
expect(value).toBeCloseTo(0.3, 5);      // For floating point

// Strings
expect(string).toMatch(/pattern/);
expect(string).toContain('substring');

// Arrays
expect(array).toContain(item);
expect(array).toHaveLength(3);

// Objects
expect(object).toHaveProperty('key');
expect(object).toHaveProperty('key', 'value');
expect(object).toMatchObject({ partial: 'match' });

// Errors
expect(() => fn()).toThrow();
expect(() => fn()).toThrow(Error);
expect(() => fn()).toThrow('message');

// Async
await expect(asyncFn()).resolves.toBe(expected);
await expect(asyncFn()).rejects.toThrow();
```

## Testing Async Code

### Promises

```javascript
test('async function resolves correctly', async () => {
  const result = await asyncFunction();
  expect(result).toBe('expected');
});

test('async function rejects on error', async () => {
  await expect(asyncFunction('bad')).rejects.toThrow('Error');
});
```

### Callbacks

```javascript
test('callback is called with result', (done) => {
  callbackFunction((result) => {
    expect(result).toBe('expected');
    done();
  });
});
```

## Mocking

### Mock Functions

```javascript
const mockFn = jest.fn();

// Set return value
mockFn.mockReturnValue('value');
mockFn.mockResolvedValue('async value');
mockFn.mockRejectedValue(new Error('error'));

// Verify calls
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
expect(mockFn).toHaveBeenCalledTimes(2);
```

### Mock Modules

```javascript
// Mock entire module
jest.mock('../path/to/module');

// Mock with implementation
jest.mock('../path/to/module', () => ({
  functionA: jest.fn().mockReturnValue('mocked'),
  functionB: jest.fn()
}));

// Clear mocks between tests
beforeEach(() => {
  jest.clearAllMocks();
});
```

### Mock Time

```javascript
beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

test('timeout behavior', () => {
  const callback = jest.fn();
  setTimeout(callback, 1000);

  jest.advanceTimersByTime(1000);
  expect(callback).toHaveBeenCalled();
});
```

## Test Fixtures

```javascript
// tests/fixtures/testData.js
module.exports = {
  validUser: {
    id: 1,
    name: 'Test User',
    email: 'test@example.com'
  },
  invalidUser: {
    id: null,
    name: '',
    email: 'invalid-email'
  }
};

// Usage in tests
const { validUser, invalidUser } = require('../fixtures/testData');

test('validates user correctly', () => {
  expect(validateUser(validUser)).toBe(true);
  expect(validateUser(invalidUser)).toBe(false);
});
```

## Integration Tests

```javascript
const request = require('supertest');
const app = require('../../app');
const db = require('../../app/database');

describe('User API', () => {
  beforeAll(async () => {
    await db.connect();
  });

  afterAll(async () => {
    await db.close();
  });

  beforeEach(async () => {
    await db.clear('users');
  });

  test('POST /users creates new user', async () => {
    const response = await request(app)
      .post('/users')
      .send({ name: 'Test', email: 'test@example.com' })
      .expect(201);

    expect(response.body).toHaveProperty('id');
    expect(response.body.name).toBe('Test');
  });

  test('GET /users/:id returns user', async () => {
    const user = await db.insert('users', { name: 'Test' });

    const response = await request(app)
      .get(`/users/${user.id}`)
      .expect(200);

    expect(response.body.name).toBe('Test');
  });
});
```

## Coverage Goals

| Category | Target |
|----------|--------|
| Critical paths | 100% |
| Business logic | 90%+ |
| Error handling | 80%+ |
| Edge cases | 70%+ |
| Utilities | 50%+ |

## Running Tests

```bash
# Run all tests
npm test

# Run specific file
npm test -- tests/unit/utils.test.js

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Run only changed tests
npm test -- --onlyChanged
```

## Test Quality Checklist

- [ ] Tests are independent (no shared state)
- [ ] Tests are deterministic (same result every run)
- [ ] Tests are fast (< 100ms for unit tests)
- [ ] Tests are readable (clear what's being tested)
- [ ] Tests cover happy path
- [ ] Tests cover edge cases
- [ ] Tests cover error cases
- [ ] Mocks are appropriate (not over-mocking)
- [ ] No console.log in tests
- [ ] No skipped tests without explanation
