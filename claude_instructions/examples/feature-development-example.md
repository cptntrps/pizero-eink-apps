# Feature Development Workflow Example

**Scenario:** Add dark mode toggle to application settings
**Project Type:** Next.js Web Application (TypeScript)
**Mode:** Standard
**Estimated Time:** 2-3 hours

---

## Context

**User Request:**
> "Add a dark mode feature. Users should be able to toggle between light and dark themes from the settings page. The choice should persist across sessions."

**Requirements:**
- Toggle button in settings page
- Dark mode affects entire app
- Preference saved (localStorage or database)
- Smooth transition between themes
- Accessible (keyboard + screen reader)

---

## Step-by-Step Walkthrough

### Step 1: Understand Requirements

**Clarifying questions:**
- Should dark mode be default for first-time users? **No, light mode default**
- System preference detection? **Yes, respect prefers-color-scheme**
- Gradual rollout or all users? **All users immediately**

**Technical decisions:**
- Storage: localStorage (fast, no backend needed)
- Implementation: CSS variables + React context
- Accessibility: WCAG AA compliant
- Animation: Smooth 200ms transition

**Acceptance criteria:**
1. Toggle renders in settings page
2. Clicking toggle changes theme immediately
3. Theme persists across page refreshes
4. All components adapt to dark mode
5. Accessible via keyboard (Tab + Enter)
6. Screen reader announces theme changes

---

### Step 2: Write Tests First (TDD)

**Create test file:**

```typescript
// src/components/ThemeToggle.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeToggle } from './ThemeToggle';
import { ThemeProvider } from '@/context/ThemeContext';

describe('ThemeToggle', () => {
  it('renders toggle button', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    expect(screen.getByRole('button', { name: /theme/i })).toBeInTheDocument();
  });

  it('toggles theme when clicked', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggle = screen.getByRole('button');

    // Initial state: light mode
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');

    // Click to dark mode
    fireEvent.click(toggle);
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');

    // Click back to light mode
    fireEvent.click(toggle);
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });

  it('persists theme to localStorage', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggle = screen.getByRole('button');

    fireEvent.click(toggle);

    expect(localStorage.getItem('theme')).toBe('dark');
  });

  it('loads saved theme from localStorage', () => {
    localStorage.setItem('theme', 'dark');

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('respects system preference when no saved theme', () => {
    // Mock system preference for dark mode
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    }));

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('is keyboard accessible', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggle = screen.getByRole('button');

    // Focus the toggle
    toggle.focus();
    expect(toggle).toHaveFocus();

    // Press Enter to toggle
    fireEvent.keyDown(toggle, { key: 'Enter' });
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('announces theme changes to screen readers', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggle = screen.getByRole('button');

    fireEvent.click(toggle);

    // Check aria-live region for announcement
    expect(screen.getByRole('status')).toHaveTextContent(/dark mode activated/i);
  });
});
```

**Run tests (they will fail - no implementation yet):**

```bash
npm test -- ThemeToggle.test.tsx

FAIL src/components/ThemeToggle.test.tsx
  7 failing tests

Error: Cannot find module '@/context/ThemeContext'
```

**Expected failure.** ✅ Tests are ready.

---

### Step 3: Implement the Feature

**3.1 Create Theme Context:**

```typescript
// src/context/ThemeContext.tsx

'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);

    // Load saved theme or detect system preference
    const savedTheme = localStorage.getItem('theme') as Theme | null;

    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
      // Respect system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const systemTheme = prefersDark ? 'dark' : 'light';
      setTheme(systemTheme);
      document.documentElement.setAttribute('data-theme', systemTheme);
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  // Prevent flash of unstyled content
  if (!mounted) {
    return null;
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

**3.2 Create Toggle Component:**

```typescript
// src/components/ThemeToggle.tsx

'use client';

import { useTheme } from '@/context/ThemeContext';
import { Moon, Sun } from 'lucide-react';
import { useState } from 'react';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const [announcement, setAnnouncement] = useState('');

  const handleToggle = () => {
    toggleTheme();

    // Announce to screen readers
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setAnnouncement(`${newTheme === 'dark' ? 'Dark' : 'Light'} mode activated`);

    // Clear announcement after 1 second
    setTimeout(() => setAnnouncement(''), 1000);
  };

  return (
    <>
      <button
        onClick={handleToggle}
        className="theme-toggle"
        aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        aria-pressed={theme === 'dark'}
      >
        {theme === 'light' ? (
          <Moon className="icon" />
        ) : (
          <Sun className="icon" />
        )}
        <span className="label">
          {theme === 'light' ? 'Dark' : 'Light'} Mode
        </span>
      </button>

      {/* Screen reader announcements */}
      <div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>
    </>
  );
}
```

**3.3 Add CSS Variables for Theming:**

```css
/* src/styles/theme.css */

:root[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #000000;
  --text-secondary: #666666;
  --border-color: #e0e0e0;
  --shadow: rgba(0, 0, 0, 0.1);
}

:root[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --text-primary: #ffffff;
  --text-secondary: #b0b0b0;
  --border-color: #404040;
  --shadow: rgba(0, 0, 0, 0.3);
}

* {
  transition: background-color 200ms ease, color 200ms ease, border-color 200ms ease;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 200ms ease;
}

.theme-toggle:hover {
  background-color: var(--border-color);
}

.theme-toggle:focus-visible {
  outline: 2px solid var(--text-primary);
  outline-offset: 2px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

**3.4 Add to Settings Page:**

```typescript
// src/app/settings/page.tsx

import { ThemeToggle } from '@/components/ThemeToggle';

export default function SettingsPage() {
  return (
    <div className="settings-page">
      <h1>Settings</h1>

      <section className="setting-section">
        <h2>Appearance</h2>
        <div className="setting-item">
          <div>
            <h3>Theme</h3>
            <p>Choose between light and dark mode</p>
          </div>
          <ThemeToggle />
        </div>
      </section>

      {/* Other settings... */}
    </div>
  );
}
```

**3.5 Wrap App with ThemeProvider:**

```typescript
// src/app/layout.tsx

import { ThemeProvider } from '@/context/ThemeContext';
import './styles/theme.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

---

### Step 4: Verify Tests Pass

**Run feature tests:**

```bash
npm test -- ThemeToggle.test.tsx

PASS src/components/ThemeToggle.test.tsx
  ✓ renders toggle button (85ms)
  ✓ toggles theme when clicked (120ms)
  ✓ persists theme to localStorage (95ms)
  ✓ loads saved theme from localStorage (110ms)
  ✓ respects system preference when no saved theme (140ms)
  ✓ is keyboard accessible (100ms)
  ✓ announces theme changes to screen readers (115ms)

Tests: 7 passed
```

**Run full test suite:**

```bash
npm test

Test Suites: 24 passed, 24 total
Tests:       194 passed, 194 total
Coverage:    79.2% (above 70% minimum) ✓
```

**Linting and types:**

```bash
npm run lint
✓ 0 errors, 0 warnings

npm run typecheck
✓ No type errors
```

---

### Step 5: Manual Testing

**Test checklist:**

- [x] Toggle appears in /settings page
- [x] Clicking toggle switches theme immediately
- [x] Theme persists after page refresh
- [x] Theme persists after browser restart
- [x] System preference respected (no saved theme)
- [x] All pages adapt to dark mode correctly
- [x] Smooth 200ms transition animation
- [x] Keyboard accessible (Tab to focus, Enter to toggle)
- [x] Screen reader announces "Dark mode activated"
- [x] Works on Chrome, Firefox, Safari
- [x] Works on mobile devices

**Performance check:**

```bash
npm run build
npm run start

Lighthouse Score:
- Performance: 98/100
- Accessibility: 100/100 ✓
- Best Practices: 100/100
- SEO: 100/100
```

---

### Step 6: Security Review

**Security checklist:**

- ✅ No XSS risk (theme is 'light' | 'dark' enum, not arbitrary string)
- ✅ localStorage only stores theme preference (no sensitive data)
- ✅ No external dependencies introduced
- ✅ No inline scripts (CSP compliant)
- ✅ ARIA attributes properly used

---

### Step 7: Commit & Document

**Stage changes:**

```bash
git add src/components/ThemeToggle.tsx
git add src/components/ThemeToggle.test.tsx
git add src/context/ThemeContext.tsx
git add src/app/layout.tsx
git add src/app/settings/page.tsx
git add src/styles/theme.css
```

**Commit:**

```bash
git commit -m "feat(ui): add dark mode toggle to settings

Implement dark mode feature with theme persistence and accessibility.

Features:
- Theme toggle in settings page
- Persists choice to localStorage
- Respects system preference (prefers-color-scheme)
- Smooth 200ms transitions
- Full keyboard accessibility
- Screen reader announcements
- CSS variables for theme consistency

Components:
- ThemeProvider context for global state
- ThemeToggle component with icon and label
- Theme CSS variables for light/dark modes

Accessibility:
- WCAG AA compliant
- Keyboard navigation (Tab + Enter)
- ARIA labels and live regions
- Focus indicators

Tests:
- 7 new tests covering all functionality
- Coverage: 79.2% (maintained above 70%)
- All existing tests still passing

Closes: #312 (Dark mode feature request)"
```

**Push:**

```bash
git push origin feat/dark-mode-toggle
```

---

### Step 8: Create Pull Request

**PR Description:**

```markdown
## Dark Mode Feature

### Summary
Adds dark mode toggle to settings page with theme persistence and full accessibility support.

### Changes
- ✨ New ThemeProvider context for global theme management
- ✨ ThemeToggle component in settings
- 🎨 CSS variables for consistent theming
- ♿ Full WCAG AA accessibility
- 💾 LocalStorage persistence
- 🎨 Smooth 200ms transitions

### Screenshots
[Light Mode] [Dark Mode]

### Testing
- ✅ 7 new tests (all passing)
- ✅ Coverage maintained at 79.2%
- ✅ Manual testing on Chrome, Firefox, Safari
- ✅ Lighthouse accessibility: 100/100
- ✅ Keyboard navigation tested
- ✅ Screen reader tested (NVDA, VoiceOver)

### Checklist
- [x] Tests added and passing
- [x] Linting passes
- [x] Type checking passes
- [x] Accessibility verified
- [x] Security reviewed
- [x] Documentation updated
- [x] Conventional commit format

### Closes
#312
```

---

## Summary

### What We Built

1. ✅ Theme context for global state
2. ✅ Toggle component with icons
3. ✅ CSS variable theming system
4. ✅ LocalStorage persistence
5. ✅ System preference detection
6. ✅ Full accessibility (keyboard + screen reader)
7. ✅ Smooth animations
8. ✅ Comprehensive tests

### Time Breakdown

- Requirements clarification: 10 min
- Write tests (TDD): 30 min
- Implement ThemeContext: 25 min
- Implement ThemeToggle: 20 min
- Add CSS theming: 20 min
- Integration: 15 min
- Manual testing: 25 min
- Security review: 10 min
- Documentation: 15 min

**Total: 2 hours 50 minutes** (within estimate)

### Non-Negotiables Verified

- ✅ All tests pass (194/194)
- ✅ Coverage 79.2% (> 70%)
- ✅ Zero linting errors
- ✅ Type checking passed
- ✅ No security vulnerabilities
- ✅ Conventional commit format
- ✅ Feature branch (not main)

### Key Decisions

1. **TDD Approach:** Tests written first, drove implementation
2. **CSS Variables:** Flexible, performant theming solution
3. **LocalStorage:** Simple persistence without backend
4. **Context API:** Appropriate for global theme state
5. **Accessibility First:** WCAG AA from the start, not afterthought

---

## Related Documentation

- **[Feature Development Workflow](../workflows/feature-development.md)** - Full workflow guide
- **[Testing Standards](../standards/testing-standards.md)** - Test requirements
- **[Security Checklist](../standards/security-checklist.md)** - Security review process

---

**This example demonstrates:** Test-driven development, incremental implementation, accessibility considerations, and thorough validation - all while maintaining non-negotiable quality standards.
