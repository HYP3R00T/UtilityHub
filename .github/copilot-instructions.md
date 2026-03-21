# GitHub Copilot Development Workflow & Standards

This document defines the complete development workflow, coding standards, and quality requirements for all code modifications, package creation, and updates in UtilityHub.

---

## 🎯 Core Principles

1. **Quality First** - Code quality, type safety, and testing are non-negotiable
2. **Follow Workflow** - Never skip steps; the exact order (Code → Tests → Type Check → Verify) is mandatory
3. **Be Explicit** - Only create tests/documentation when explicitly requested; when asked, make it comprehensive
4. **Stay Modern** - Use Python 3.12+ exclusively; leverage modern typing and idioms
5. **Zero Warnings** - Type checker must pass with zero errors and zero warnings

---

## 📋 Development Workflow

Follow this workflow **every single time** for any code modifications, new packages, or updates. Do not skip any step.

### Phase 1: Code Implementation

Implement all code changes with full adherence to standards.

**Requirements:**
- Follow all **Coding Standards** listed below strictly
- Use proper type hints on every function argument and return value
- Implement complete functionality with correct logic
- Write clean, maintainable, idiomatic Python code
- No temporary solutions, placeholder code, or incomplete implementations
- No `Any` types without explicit justification

**Python Version:**
- Use Python 3.12+ exclusively
- Use modern syntax and built-in generics (e.g., `list[str]`, not `List[str]`)
- No compatibility with older Python versions

### Phase 2: Testing

Verify all tests pass before proceeding to type checking.

**When NOT to create tests:**
- Unless the user explicitly asks to "create tests," "write tests," or "add test coverage"
- Do not automatically create tests for every code change

**When to check existing tests:**
- Always locate and run existing test files for modified code
- Execute `pytest` to ensure all existing tests still pass
- Assess whether existing coverage is sufficient for the changes

**When user explicitly requests tests:**
- Create comprehensive test suites covering:
  - **Happy path**: Normal operation with typical inputs
  - **Edge cases**: Boundary conditions, empty inputs, extreme values
  - **Error cases**: Invalid inputs, exceptions, failure scenarios
  - **Validation**: Type checking, constraint enforcement
- Use `pytest` framework
- Include clear, descriptive test names and docstrings
- Test names follow pattern: `test_<function>_<scenario>`

**Final step:**
- Run complete test suite: `pytest` must pass with all tests succeeding

### Phase 3: Type Safety Validation

Ensure all type hints are correct and comprehensive.

**Required actions:**
1. Execute `mise run check` to validate all type hints
2. Address **every** error and warning reported:
   - No uncovered union types (all branches must have explicit types)
   - No missing return type hints (all functions must declare return type)
   - No type mismatches (parameter/return types must align)
   - No `Any` types without explicit justification in a comment
3. Re-run `mise run check` and confirm: **"All checks passed!"**

**Quality bar:**
- Zero errors
- Zero warnings
- 100% type coverage (no implicit `Any`)

### Phase 4: Final Verification

Confirm all quality gates are met before marking work complete.

**Pre-completion checklist:**
- ✅ All code implemented per Coding Standards
- ✅ All tests pass (`pytest` runs successfully)
- ✅ Type checker passes cleanly (`mise run check` → "All checks passed!")
- ✅ No unresolved TODOs or temporary comments
- ✅ Code follows all naming conventions
- ✅ Docstrings are complete and accurate

---

## 🔧 Coding Standards

### Python Version & Modern Features
- **Minimum version**: Python 3.12
- **Always use**: Modern syntax (walrus operator, built-in generics, union syntax with `|`)
- **Never use**: Backport imports (`List`, `Dict` from `typing`); use `list`, `dict` instead
- **String formatting**: Always use f-strings
- **Path handling**: Always use `pathlib.Path`, never `os.path`

### Naming Conventions
- **Variables, functions, methods**: `snake_case`
- **Classes, exceptions**: `PascalCase`
- **Module-level constants**: `ALL_CAPS`
- **Private/unused identifiers**: Prefix with underscore (`_`)
- **File names**: `snake_case`

### Type Safety (Mandatory)
- **Every function**: Must have complete type hints
  - All parameters must have type hints
  - Return type must be explicitly declared
  - No implicit `Any`
- **All variables**: Type hints on class attributes and complex local variables
- **Modern types**:
  - Use `list[str]`, `dict[str, int]`, `tuple[int, ...]` (built-in generics)
  - Use `T | None` for optional values (not `Optional[T]`)
  - Use `Literal["a", "b"]` for fixed string/enum values
  - Use `TypedDict` or Pydantic models for structured data
- **Union types**: Always cover all branches; no incomplete union handling
- **Return types**: Be specific (e.g., `list[MyModel]`, not `list`)

### Error Handling
- **Always use specific exception types** (e.g., `ValueError`, `FileNotFoundError`, custom exceptions)
- **Never use bare `except:`** - always catch specific exceptions
- **Error messages**: Provide clear, actionable information about what went wrong
- **External failures**: Handle I/O, database, and API errors gracefully
- **Logging**: Use `logging` module with appropriate levels (`info`, `warning`, `error`, `critical`)

### Code Organization & Style
- **PEP 8 compliance**: Follow [PEP 8](https://peps.python.org/pep-0008/) strictly
- **Import organization**:
  1. Standard library
  2. Third-party libraries
  3. Local modules
- **Function/class size**: Keep small and focused; max ~50 lines for functions, ~200 lines for classes
- **Code formatting**: Use `ruff format` for consistent formatting
- **Linting**: Use `ruff` for linting; fix all warnings
- **Line length**: Maximum 100 characters (enforced by formatter)

### Data Modeling (Pydantic)
- **Always use Pydantic** for configuration, API contracts, and data validation
- **Strict types**: Every model field must have an explicit type (no `Any`)
- **Field metadata**: Use `field(default=..., alias=..., description=...)` for clarity
- **Model configuration**: Use `model_config = ConfigDict(...)` for validation behavior
- **Validators**: Use `@field_validator` and `@model_validator` for complex logic
- **Immutability**: Use `frozen=True` if the model should not be mutable
- **Modern methods**: Use `model.model_dump()` and `model.model_validate()` (not `.dict()`, `.parse_obj()`)

### Docstrings
- **Google-style docstrings** for all public functions, classes, and modules
- **Required sections**: Args, Returns, Raises (if applicable), Examples (if helpful)
- **Parameter docs**: Describe type, purpose, and constraints
- **Return docs**: Describe what is returned and in what format
- **Exception docs**: List all exceptions that can be raised
- **No TODO comments**: Keep docstrings clean; use issues for improvements

---

## 📝 Documentation Standards

### When NOT to create documentation
- Do not create README files, guides, or docstrings unless explicitly requested
- Do not add examples, API docs, or comments beyond basic function docstrings
- Do not generate architecture or usage guides

### When documentation IS requested
- Create **complete and comprehensive** documentation
- Include all relevant sections:
  - Overview/description of purpose
  - Installation/setup instructions (if applicable)
  - Quick start example
  - API reference with all functions/classes
  - Configuration examples
  - Error handling and troubleshooting
  - Known limitations
- Use clear, accessible language
- Include code examples that work and are tested
- Ensure consistency in formatting and terminology

---

## 🧪 Testing Standards

### When NOT to create tests
- Do not create test files or test cases unless explicitly requested
- Do not add test coverage "just in case"

### When tests ARE explicitly requested
- Create **comprehensive test suites** covering:
  1. **Happy path**: Normal operation with typical valid inputs
  2. **Edge cases**: Boundary conditions, empty/null values, min/max values
  3. **Error cases**: Invalid inputs, exceptions, failure scenarios
  4. **Validation**: Type validation, constraint enforcement, cross-field validation
- **Test structure**:
  - Use `pytest` framework exclusively
  - Clear, descriptive test names: `test_<function>_<scenario>`
  - Include docstrings explaining what is being tested
  - Each test should test one thing
  - Use fixtures for setup/teardown
  - Mock external dependencies
- **Coverage requirements**:
  - All code paths should be exercised
  - All exception types should be tested
  - All validation rules should be verified
- **Quality**:
  - Tests must be deterministic (same result every run)
  - Tests must be isolated (no dependencies between tests)
  - Tests must be fast (no unnecessary I/O)
  - All tests must pass before marking work complete

---

## ✅ Workflow Execution Checklist

### Before submitting any work, verify ALL items:

#### 🔨 Implementation Phase
- [ ] All code follows Coding Standards above
- [ ] Python 3.12+ syntax used exclusively
- [ ] All functions have complete type hints (args + return)
- [ ] All class attributes have type hints
- [ ] No `Any` types without justification comment
- [ ] Code is clean, readable, and idiomatic
- [ ] No placeholder or temporary code remains
- [ ] Docstrings are complete (Google-style)
- [ ] All imports organized properly

#### 🧪 Testing Phase
- [ ] Identified all relevant existing test files
- [ ] Ran `pytest` and all existing tests pass
- [ ] Assessed code coverage for changes
- [ ] If user requested tests: comprehensive test suite created
  - [ ] Happy path scenarios covered
  - [ ] Edge cases tested
  - [ ] Error conditions tested
  - [ ] Validation verified
  - [ ] Test names are clear and descriptive
  - [ ] All tests pass

#### 🔒 Type Safety Phase
- [ ] Executed `mise run check` successfully
- [ ] **Zero errors** reported
- [ ] **Zero warnings** reported
- [ ] All union types properly handled
- [ ] All return types explicit and specific
- [ ] No implicit `Any` types remain
- [ ] Re-ran `mise run check` final confirmation

#### ✨ Final Verification
- [ ] All existing tests still pass
- [ ] All new tests pass (if created)
- [ ] Type checker passes cleanly
- [ ] Code follows all naming conventions
- [ ] Docstrings complete and accurate
- [ ] No unresolved TODOs or FIXMEs
- [ ] Code is production-ready

---

## 🚫 Critical Rules (Non-Negotiable)

1. **Workflow order is mandatory** - Code → Tests (if requested) → Type Check → Verify. Never skip or reorder.

2. **Type safety is mandatory** - `mise run check` must pass with zero errors and zero warnings. Period.

3. **Python 3.12+ only** - Use modern syntax; no compatibility with older versions.

4. **No implicit `Any`** - Every type must be explicit. Comments required if `Any` is necessary.

5. **Tests only when asked** - Do not create tests unless user explicitly requests them. When asked, be comprehensive.

6. **Documentation only when asked** - Do not create guides/READMEs unless user explicitly requests them. When asked, be complete.

7. **Fix code, not tests** - If a test fails, the code is wrong. Debug and fix the implementation.

8. **All standards are requirements, not suggestions** - Follow Coding Standards exactly; they exist for a reason.

9. **Complete implementations only** - No TODOs, no temporary solutions, no incomplete features.

10. **Zero warnings on type checker** - One warning is a failure. Find and fix every single one.

---

## 📌 Workflow Summary

```
START
  ↓
IMPLEMENT CODE (follow all Coding Standards, full type hints)
  ↓
RUN EXISTING TESTS (pytest)
  ↓
IF user requested tests → CREATE COMPREHENSIVE TESTS → RUN ALL TESTS
ELSE → SKIP TO NEXT STEP
  ↓
RUN TYPE CHECKER (mise run check)
  ↓
ANY ERRORS/WARNINGS? → YES → FIX → RUN AGAIN
                    → NO → CONTINUE
  ↓
FINAL VERIFICATION (check all items above)
  ↓
COMPLETE & READY FOR MERGE
```

---

## 🔍 When in Doubt

- **"Should I create a test?"** → Only if explicitly asked. If asked, cover everything.
- **"Should I write documentation?"** → Only if explicitly asked. If asked, be thorough.
- **"Is this type hint specific enough?"** → If you're not sure, it's not specific enough.
- **"Should I commit with a warning?"** → Absolutely not. Fix it first.
- **"Can I skip type checking?"** → No. Type safety is mandatory.
- **"Can I use `Any`?"** → Only with a comment explaining why it's necessary.
- **"Should I follow the workflow order?"** → Always. It's non-negotiable.
