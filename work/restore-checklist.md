# Restore Old UI + Full Feature Fix - Progress Checklist

## Project setup & branch (1–6)
- [x] 1. Create branch `restore/old-ui-20250916` from current main
- [x] 2. Pull old UI branch/files for reference
- [x] 3. Add work/ checklist file to track progress 
- [ ] 4. Run npm ci/pnpm install and start dev server
- [ ] 5. Add automated pre-commit hooks if missing
- [ ] 6. Run unit tests and note failing tests

## Visual parity: Home screen (7–20)
- [ ] 7. Replace new Home layout with exact screenshot layout
- [ ] 8. Move Quick Actions above Inventory Health & Smart Insights
- [ ] 9. Match site title, subtitle, fonts, spacing, icons exactly
- [ ] 10. Implement "Your Items" preview: 3-4 items with thumbnail/name/qty/expiry
- [ ] 11. Add "View All" link beneath preview → navigate to Inventory page
- [ ] 12. Ensure Inventory Health and Smart Insights below Quick Actions
- [ ] 13. Align header buttons to match screenshot
- [ ] 14. Implement bottom FAB with menu: Add Manual, Take Photo, Upload Receipt, Scan Barcode
- [ ] 15. FAB toggle open/close with animation
- [ ] 16. Ensure responsive at mobile widths
- [ ] 17. Remove duplicate Add Item header buttons
- [ ] 18. Add micro-animations to Quick Actions hover/active
- [ ] 19. Ensure Quick Actions keyboard accessible with aria-label
- [ ] 20. Fix layout shift/overflow vs bottom nav - safe area

## Inventory: add/edit/delete + counters (21–36)
- [ ] 21. Fix Add Item manual form persistence to real store
- [ ] 22. Fix "Add first item" bug - detect inventory length > 0
- [ ] 23. Ensure "Expiring Soon" counter computes correctly
- [ ] 24. Add visual badge showing count next to Expiring Soon
- [ ] 25. Implement inventory table/list page matching screenshot
- [ ] 26. Add edit-in-place for item name/qty/expiry with validation
- [ ] 27. Add delete with confirmation dialog
- [ ] 28. Add merge/duplicate detection for similar items
- [ ] 29. Ensure inventory changes update Home preview immediately
- [ ] 30. Add unit tests for inventory add/edit/delete and expiry logic
- [ ] 31. Show item thumbnail if image present; placeholder otherwise
- [ ] 32. Handle offline add: queue to local storage, sync when online
- [ ] 33. Add last-modified timestamp in item details

## Receipt OCR & Upload flow (37–60)
- [ ] 34. Replace static placeholder with proper OCR pipeline (Tesseract.js)
- [ ] 35. Implement robust image reading: FileReader → dataURL → OCR worker
- [ ] 36. Implement OCR text cleaning: normalize whitespace, fix OCR mistakes
- [ ] 37. Implement item-line extraction rules (regex heuristics) 
- [ ] 38. Build keyword blacklist: total, sum, amount, subtotal, etc.
- [ ] 39. Build whitelist/heuristic for line-items
- [ ] 40. Compute confidence score per parsed item, display in UI
- [ ] 41. Provide UI to edit parsed line-items before adding
- [ ] 42. Persist each added item with receiptRef and rawText
- [ ] 43. Add OCR progress UI with animation and cancel option
- [ ] 44. Add unit tests for OCR parser heuristics
- [ ] 45. Add fallback: if OCR fails, show manual-add form
- [ ] 46. Ensure receipt extraction works different orientations/resolutions
- [ ] 47. Fix extracted item list cut-off behind bottom nav
- [ ] 48. Add swipe gestures: right to add, left to remove (with animation)
- [ ] 49. Add toasts for actions: "Item added", "Removed", "Failed to extract"
- [ ] 50. If server-side OCR, implement retries & error messages

## Camera support (critical) — all 3 entry points (51–62)
- [ ] 51. Centralize camera code into single CameraCapture module
- [ ] 52. Use navigator.mediaDevices.getUserMedia with environment facing
- [ ] 53. Handle permissions: request, denial, guidance, fallback to upload
- [ ] 54. Detect Android WebView/PWA, use legacy approach if needed
- [ ] 55. Add AndroidManifest CAMERA permission for Capacitor builds
- [ ] 56. For barcode scanning use @zxing/library or jsQR with camera stream
- [ ] 57. Provide explicit UI flows: preview, capture, confirm/cancel, OCR/barcode
- [ ] 58. Fallback: if getUserMedia unsupported, show upload button
- [ ] 59. Ensure camera works on mobile Chrome (test Android device)
- [ ] 60. Add unit/integration tests for camera availability scenarios
- [ ] 61. Ensure camera stream cleanup (stop tracks) on close
- [ ] 62. For barcode scanning, allow manual input if lookup fails

## Barcode scanning & product lookup (63–70)
- [ ] 63. Implement Scan Barcode using camera module and barcode library
- [ ] 64. On successful scan, lookup product locally then public API
- [ ] 65. Populate add form with product name, suggest qty/unit/price
- [ ] 66. Provide "Add manually" option if lookup returns nothing
- [ ] 67. Add tests for barcode scanning flow
- [ ] 68. Add UI feedback if barcode scanning times out
- [ ] 69. Persist barcode value in item record
- [ ] 70. Document Android testing steps for reviewer

## Recipes & Meal Planner (71–76)
- [ ] 71. Ensure Recipes page UI matches screenshot, functions wired
- [ ] 72. Smart Recipes: implement matching algorithm from current inventory
- [ ] 73. Show match percentage and missing ingredients with add-to-shopping
- [ ] 74. Wire Meal Planner: plan meals, reserve quantities when adding
- [ ] 75. Ensure top toolbar buttons functional and linked
- [ ] 76. Add tests for recipe matching logic

## Shopping & Family tabs (77–83)
- [ ] 77. Recreate Shopping/Family UIs per provided screenshots
- [ ] 78. Implement shopping lists: add/remove items, group by recipe, check/uncheck
- [ ] 79. Implement family sharing: invite by email/link stub
- [ ] 80. Make Shopping/Family tabs fully functional: click items, edit qty, mark purchased
- [ ] 81. Add persistence for shopping lists
- [ ] 82. Add unit tests and e2e tests for shopping flows
- [ ] 83. Consider enhancements: share lists via link, sync state

## Settings & Theme (84–90)
- [ ] 84. Fix Appearance toggles: Light/Dark/System switch whole-app theme
- [ ] 85. Ensure System follows OS-level theme via prefers-color-scheme
- [ ] 86. Fix stray "force dark" / misplaced labels - implement or remove
- [ ] 87. Move Save Changes button to bottom or add floating Save
- [ ] 88. Add onChange handlers to all controlled checkboxes
- [ ] 89. Persist settings (theme, notifications, units) to storage
- [ ] 90. Add tests to verify theme toggling and persistence

## UI/UX polish & accessibility (91–98)
- [ ] 91. Ensure all modals have safe bottom padding vs bottom nav
- [ ] 92. Fix text fields popup background/text color in light/dark themes
- [ ] 93. Implement animations: spinner, swipe animations, add/remove transitions
- [ ] 94. Ensure color contrast meets accessibility guidelines
- [ ] 95. Add keyboard accessibility and focus management for FAB
- [ ] 96. Add aria-labels and roles for major interactive elements
- [ ] 97. Add i18n-ready text keys (English only for now)
- [ ] 98. Provide graceful fallback messages for errors

## Testing: unit, integration, e2e & manual (99–106)
- [ ] 99. Add unit tests: inventory logic, expiry counter, OCR parser, barcode handling
- [ ] 100. Implement e2e tests with Playwright: Add item, receipt OCR, camera capture, recipe search, shopping
- [ ] 101. Write tests asserting Quick Actions appear above Inventory Health on Home
- [ ] 102. Add visual snapshot tests for Home, Inventory, Recipes
- [ ] 103. Provide scripts for local Android camera emulation if possible
- [ ] 104. Implement CI job to run tests on PR
- [ ] 105. Provide manual QA checklist with step-by-step reproduction
- [ ] 106. Run tests and fix breaking issues until green

## Code hygiene, docs & PR (107–112)
- [ ] 107. Break work into small commits with clear messages
- [ ] 108. Add CHANGELOG entry describing restore + fixes
- [ ] 109. Update README with new dev instructions (Android testing, camera permissions)
- [ ] 110. Create PR with description, screenshots before/after, QA checklist
- [ ] 111. Attach test run logs and screenshots in PR
- [ ] 112. Mark PR ready for review only after all tests pass locally and e2e

## Final verification & production readiness (113–120)
- [ ] 113. Manually test entire app on Desktop Chrome
- [ ] 114. Manually test all camera flows on real Android device (Chrome)
- [ ] 115. Ensure Add/Edit/Delete inventory works and persists across reloads
- [ ] 116. Validate Recipes, Shopping, Family flows and functional buttons
- [ ] 117. Ensure Settings theme toggles work and persist
- [ ] 118. Ensure no console errors in production build (next build && next start)
- [ ] 119. Create final QA report with screenshots & Android camera video clip
- [ ] 120. Merge PR only after all checks and create release note

## QA Checklist (Manual Testing)
- [ ] Launch app (dev mode) and navigate to Home
- [ ] Quick Actions appear above Inventory Health
- [ ] Home shows "Your Items" preview (3–4 items). Click "View All" → Inventory page opens
- [ ] Add Item (Manual) → item appears immediately in Home preview and Inventory (reload to confirm)
- [ ] Add Item (Take Photo) on Desktop → camera opens, capture, preview, OCR extracts items, add some items → persisted
- [ ] Add Item (Take Photo) on Android device → camera opens, capture, OCR works, items persist
- [ ] Upload receipt (file) → OCR extracts items (no total/discount/address lines)
- [ ] Parsed item list shows Edit / Remove / Add buttons; swipe left/right works with animation
- [ ] Scan Barcode → camera opens, barcode decoded, lookup pre-fills add form → persisted
- [ ] Recipes page: Smart recipes show matches from inventory; can add missing ingredients to shopping list
- [ ] Shopping tab: can add/remove items, check purchased, persistent
- [ ] Family tab: can invite (stub) and share lists (or actual implementation)
- [ ] Settings: toggles (notifications), theme (Light/Dark/System) work and persist
- [ ] No UI elements hidden behind bottom nav; modals and bottom-sheets show action buttons fully
- [ ] All buttons in the app are functional; no dead links
- [ ] Run unit tests & e2e tests; all pass
- [ ] Production build has no console errors

---

**Target: Production-ready — verified on Desktop and Android**