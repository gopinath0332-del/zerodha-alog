# Development Guidelines

## 🔄 Feature Parity Requirement

**IMPORTANT:** All features and bug fixes must be implemented in BOTH interfaces:

1. **Modern GUI** (`Application/gui_modern.py`)
2. **Enhanced CLI** (`Application/main_enhanced.py`)

## 📋 Checklist for Changes

When implementing any feature or bug fix, ensure you:

- [ ] Implement the change in `gui_modern.py`
- [ ] Implement the same change in `main_enhanced.py`
- [ ] Update relevant documentation
- [ ] Test both interfaces
- [ ] Verify feature parity is maintained

## 🎯 Affected Components

### Portfolio Management

- **GUI:** Portfolio tab, positions tab, holdings tab, margins tab
- **CLI:** Menu options 1-5 (Portfolio Summary, Positions, Holdings, Orders, Margins)

### Trading Operations

- **GUI:** Trading tab with order placement forms
- **CLI:** Orders submenu (options 4a-4e)

### Strategy Monitors

- **GUI:** NatgasMini tab, GOLDPETAL tab
- **CLI:** Strategy Monitors submenu (option 7)

### Tools & Utilities

- **GUI:** Tools tab
- **CLI:** Tools submenu (option 8)

### Market Data

- **GUI:** Market Data tab
- **CLI:** Market Data option (option 6)

## 🔧 Implementation Pattern

### Example: Adding a New Feature

```python
# 1. Implement in gui_modern.py
class ModernTradingGUI:
    def new_feature(self):
        # GUI implementation with DearPyGui
        pass

# 2. Implement in main_enhanced.py
class EnhancedTradingCLI:
    def new_feature(self):
        # CLI implementation with console output
        pass
```

### Example: Fixing a Bug

```python
# 1. Fix in gui_modern.py
# Before:
result = calculate_value()  # Bug: missing error handling

# After:
try:
    result = calculate_value()
except Exception as e:
    logger.error("calculation_failed", error=str(e))
    result = 0

# 2. Apply same fix in main_enhanced.py
try:
    result = calculate_value()
except Exception as e:
    logger.error("calculation_failed", error=str(e))
    result = 0
```

## 📝 Documentation Updates

When making changes, update:

1. **README.md** - If feature is user-facing
2. **ENHANCED_CLI_GUIDE.md** - For CLI-specific changes
3. **Inline comments** - In both files
4. **Docstrings** - For new functions/methods

## 🧪 Testing Requirements

Before committing:

1. **GUI Testing:**

   ```bash
   ./run_gui_modern.sh
   # Test the changed feature
   ```

2. **CLI Testing:**

   ```bash
   ./run_cli_enhanced.sh
   # Test the same feature
   ```

3. **Verify Parity:**
   - Same data displayed
   - Same functionality
   - Same error handling
   - Same notifications

## 🚨 Common Pitfalls

### ❌ Don't Do This:

```python
# Only fixing in GUI
# File: gui_modern.py
def get_positions(self):
    # Fixed bug here
    return positions
```

### ✅ Do This:

```python
# Fix in BOTH files
# File: gui_modern.py
def get_positions(self):
    # Fixed bug here
    return positions

# File: main_enhanced.py
def view_positions(self):
    # Applied same fix here
    return positions
```

## 📊 Code Reuse

When possible, extract common logic to `Core_Modules`:

```python
# Core_Modules/utils.py
def calculate_position_value(position):
    """Shared logic for both GUI and CLI"""
    return position['quantity'] * position['average_price']

# gui_modern.py
from Core_Modules.utils import calculate_position_value
value = calculate_position_value(position)

# main_enhanced.py
from Core_Modules.utils import calculate_position_value
value = calculate_position_value(position)
```

## 🔍 Review Checklist

Before creating a PR:

- [ ] Feature/fix implemented in `gui_modern.py`
- [ ] Feature/fix implemented in `main_enhanced.py`
- [ ] Both implementations tested
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Error handling consistent
- [ ] Logging consistent
- [ ] Notifications work in both

## 📌 Current Branch

**Branch:** `bugfix/position-values`

Remember to apply all changes to both interfaces!

## 💡 Tips

1. **Start with GUI:** Implement in GUI first, then port to CLI
2. **Test Incrementally:** Test each interface as you implement
3. **Keep Sync:** Don't let one interface fall behind
4. **Document Differences:** If implementations must differ, document why
5. **Code Review:** Have someone verify parity before merging

## 🎯 Goal

Maintain **100% feature parity** between Modern GUI and Enhanced CLI at all times.

---

**Last Updated:** 2025-11-25  
**Applies To:** All future development
