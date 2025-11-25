# MCP Playwright - Enhanced Browser Automation

## Overview

This project uses the **@ejazullah/mcp-playwright** package, an enhanced Model Context Protocol (MCP) server that provides comprehensive browser automation capabilities with:

- **Agents**: Test generator, healer, and planner
- **CDP Support**: Connect to existing Chrome/Chromium instances
- **Form Automation**: Comprehensive form interaction tools
- **Data Extraction**: Bulk extraction of links, images, tables
- **Accessibility**: LLM-friendly structured accessibility snapshots

## Installation

The MCP Playwright package is already installed in `tests/ui/`:

```powershell
npm install @ejazullah/mcp-playwright --save-dev
```

## Configuration

Configuration file: `mcp-configs/mcp-playwright-config.json`

## Available Agents

### 1. Test Generator Agent
**Purpose**: Automatically generates Playwright test scripts from user interactions

**Usage**:
```javascript
// The generator watches your manual interactions and creates test code
await playwright_generate_test({
  url: 'http://localhost:5173',
  outputPath: 'tests/ui/generated/dashboard_test.spec.ts',
  recordActions: true
});
```

**Output**: Generated Playwright test files in `tests/ui/generated/`

---

### 2. Test Healer Agent
**Purpose**: Automatically repairs failing tests by detecting and fixing selector issues

**Features**:
- CSS fallback strategies
- XPath fallback
- Text-based selectors
- Role-based selectors
- Max retry attempts: 3

**Usage**:
```javascript
// Healer automatically tries different selector strategies when tests fail
const result = await playwright_heal_test({
  testFile: 'tests/ui/manual_analyze.spec.ts',
  failedSelector: 'button:has-text("Analyze Now")',
  strategies: ['css_fallback', 'xpath_fallback', 'text_based', 'role_based']
});
```

**Benefits**:
- Reduces maintenance when UI changes
- Tries alternative selectors automatically
- Logs healing strategies for review

---

### 3. Test Planner Agent
**Purpose**: Plans test scenarios and generates test suites from requirements

**Features**:
- Gherkin format output
- Accessibility checks included
- Scenario planning
- Test suite generation

**Usage**:
```javascript
// Planner generates test plans from user stories or requirements
const testPlan = await playwright_plan_test({
  requirement: 'User should be able to trigger analysis and see results',
  outputFormat: 'gherkin',
  includeAccessibility: true
});
```

**Output**: Test plans in Gherkin format (Given/When/Then)

---

## Quick Start

### 1. Use with VS Code / Claude

Install the MCP server in your editor:

**VS Code**:
```bash
code --add-mcp '{"name":"playwright","command":"npx","args":["@ejazullah/mcp-playwright@latest"]}'
```

**Claude Desktop** (add to config):
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@ejazullah/mcp-playwright@latest"]
    }
  }
}
```

### 2. Run Tests with Agents

**Generate a test**:
```powershell
cd tests\ui
# Ask Claude/Copilot: "Generate a Playwright test for the Dashboard analyze button"
```

**Heal a failing test**:
```powershell
# When a test fails, ask Claude/Copilot: "Heal the failing test by trying alternative selectors"
```

**Plan a test suite**:
```powershell
# Ask Claude/Copilot: "Create a test plan for the Dashboard E2E flow"
```

### 3. Run in Headed Mode (Watch Agents Work)

```powershell
cd tests\ui
npx playwright test --headed
```

---

## Available Tools

### Navigation
- `playwright_navigate` - Navigate to URL
- `playwright_click` - Click elements
- `playwright_fill` - Fill form inputs
- `playwright_select` - Select dropdown options
- `playwright_evaluate` - Run JavaScript in page

### Interaction
- `playwright_keyboard_press` - Press keyboard keys
- `playwright_keyboard_type` - Type text
- `playwright_mouse_move` - Move mouse
- `playwright_drag_and_drop` - Drag and drop

### Inspection
- `playwright_screenshot` - Take screenshots
- `playwright_pdf` - Save as PDF
- `playwright_get_element_text` - Extract text
- `playwright_get_element_attribute` - Get attributes
- `playwright_get_element_css` - Get CSS styles

### Waiting
- `playwright_wait_for_selector` - Wait for elements
- `playwright_wait_for_navigation` - Wait for navigation
- `playwright_wait_for_load_state` - Wait for page load

### Extraction
- `playwright_get_links` - Extract all links
- `playwright_get_images` - Extract all images
- `playwright_get_tables` - Extract table data
- `playwright_extract_text` - Extract text content

### CDP (Chrome DevTools Protocol)
- `playwright_cdp_list_targets` - List CDP targets
- `playwright_cdp_connect` - Connect to browser
- `playwright_cdp_send_command` - Send CDP commands

---

## Integration with Project

### Current Test Structure
```
tests/ui/
├── manual_analyze.spec.ts       # Main E2E test
├── helpers/
│   └── dashboard-helpers.ts      # API helpers
├── generated/                    # Auto-generated tests (by Generator Agent)
├── healed/                       # Healed test versions (by Healer Agent)
└── plans/                        # Test plans (by Planner Agent)
```

### Jenkins Integration

The agents can be used in Jenkins pipelines:

```groovy
stage('QA - Playwright with Agents') {
  steps {
    dir('tests/ui') {
      sh 'npm ci'
      sh 'npx playwright install --with-deps'
      sh 'npm run test:ci:ui || npx @ejazullah/mcp-playwright heal-failing-tests'
    }
  }
}
```

---

## Troubleshooting

### Agent Not Found
Ensure the package is installed:
```powershell
cd tests\ui
npm list @ejazullah/mcp-playwright
```

### Selector Healing Not Working
Check the healer config in `mcp-playwright-config.json`:
```json
{
  "agents": {
    "test_healer": {
      "enabled": true,
      "config": {
        "retry_strategies": ["css_fallback", "xpath_fallback", "text_based", "role_based"],
        "max_attempts": 3
      }
    }
  }
}
```

### CDP Connection Issues
Ensure Chrome is running with debugging enabled:
```powershell
chrome.exe --remote-debugging-port=9222
```

---

## Documentation

- **Package**: https://www.npmjs.com/package/@ejazullah/mcp-playwright
- **GitHub**: https://github.com/ejazullah/mcp-playwright
- **MCP Protocol**: https://modelcontextprotocol.io/

---

## Next Steps

1. ✅ **Installed**: `@ejazullah/mcp-playwright` package
2. ✅ **Configured**: MCP config in `mcp-configs/mcp-playwright-config.json`
3. ⏳ **Try agents**: Ask Claude/Copilot to generate, heal, or plan tests
4. ⏳ **Integrate with CI**: Add agent commands to Jenkins pipeline
5. ⏳ **Generate tests**: Use Generator Agent for new Dashboard features

---

**Last Updated**: November 23, 2025
