# Claude Code Instructions for Morty Trades Backtesting

## Testing Protocol

**CRITICAL: Always run relevant tests BEFORE finalizing any code changes**

### Pre-Change Testing Steps:
1. **Identify affected components** - Determine which modules/functions your changes will impact
2. **Run existing tests first** - Execute tests for affected components to establish baseline
3. **Make incremental changes** - Implement changes in small, testable chunks
4. **Test after each change** - Run relevant tests immediately after each modification
5. **Fix issues immediately** - Address any test failures before proceeding

### Test Commands:
```bash
# Activate virtual environment
source .venv/bin/activate

# Run specific test classes
python -m pytest tests/unit/test_data_loader.py::TestBulkDataLoader -v
python -m pytest tests/unit/test_date_utils.py::TestDateUtils -v

# Run all unit tests
python -m pytest tests/unit/ -v

# Run all tests
python -m pytest tests/ -v
```

### Code Change Workflow:
1. **Read and understand** existing code structure
2. **Run baseline tests** to ensure current functionality works
3. **Plan changes** using TodoWrite tool for complex modifications
4. **Implement incrementally** - make small changes and test frequently
5. **Verify all tests pass** before marking changes as complete
6. **Update tests** if functionality intentionally changes

### Testing Guidelines:
- **Unit tests** should pass for any component you modify
- **Integration tests** should pass if you change interfaces between components
- **Mock external dependencies** (APIs, databases) in tests when needed
- **Test edge cases** and error conditions
- **Verify backward compatibility** unless intentionally breaking it

## Project Structure Notes:
- `/tests/unit/` - Unit tests for individual components
- `/tests/integration/` - Integration tests for component interactions
- `/core/` - Core utilities (date_utils, etc.)
- `/database/` - Database management and data loading
- Virtual environment: `.venv/` (always activate before running tests)

## Common Test Patterns:
- Use `@patch` decorators to mock external dependencies
- Mock expensive operations (API calls, file I/O, database operations)
- Test both success and failure scenarios
- Verify that mocked functions are called with expected parameters