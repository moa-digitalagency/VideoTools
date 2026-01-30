## 2024-05-23 - Accessible Actions
**Learning:** The app uses `div`s with click handlers for file uploads, which are inaccessible to keyboard users by default.
**Action:** Always add `role="button"`, `tabindex="0"`, and `onkeydown` handler for Enter/Space keys when using non-button elements for actions.
