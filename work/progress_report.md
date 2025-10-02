# Receipt Parser Progress Report

## Current Status: 1-2/11 receipts nearly perfect

### Completed Fixes ✅

1. **Flat Format Parsing** - Receipt #1 Family Restaurant now extracts all items correctly
   - Added tab/multi-space column detection
   - Flexible decimal matching (430.0 vs 430.00)
   - **Result**: 3/3 items extracted, total correct ($1060)

2. **Total Extraction with Commas** - Handles "1,060.0" format
   - Updated regex to strip commas before parsing
   - **Impact**: Multiple receipts now extract totals correctly

### Remaining Critical Issues

#### HIGH PRIORITY (blocks multiple receipts):

3. **Hierarchical Standalone Items** - Affects 4+ receipts (#3, #5, #9, #10)
   - Lines like "Pizza    $103" on their own (not indented) treated as headers instead of items
   - **Fix**: When line has price but no indent AND next line is NOT indented → standalone item

4. **Weight-Based Quantities** - Receipt #6 Grocery
   - `0.778kg NET` not being extracted as quantity
   - Currently parsing the weight pattern but defaulting qty to 1.0
   - **Fix**: Already partially implemented, needs debugging

5. **Date Format: DD-Mon-YY** - Receipt #2
   - "20-May-18 22:55" not recognized
   - **Fix**: Add pattern to _extract_date method

6. **"SPECIAL" Items** - Receipt #6
   - Lines with "SPECIAL  $0.99" blacklisted
   - **Fix**: Allow "SPECIAL" when it's the ONLY text before price

7. **Item Code Line Numbers** - Receipt #7 Lorem Shop
   - Leading numbers like "1 9275" being parsed as quantity
   - "1 9275 Bread" → qty=1 (correct) but "2 0230 Salami" → qty=2 (wrong, should be 1)
   - **Fix**: When line starts with multiple numbers, first is line number (skip it)

#### MEDIUM PRIORITY:

8. **Embedded Quantity in Name** - Receipts #5, #9
   - "2 Burritos" → qty should be 2
   - "2 GYRO" → qty should be 2
   - Currently extracting qty=1

9. **Merchant Name Heuristics** - Multiple receipts
   - Picking wrong lines (timestamps, addresses)
   - Cosmetic issue, doesn't affect item extraction

10. **Multi-line Items** - Receipt #8 Target
    - Complex case, low priority

---

## Next Actions

Given token/time constraints, implementing fixes #3-7 will achieve ~70-80% accuracy across all receipts.

### Implementation Plan:

1. Fix hierarchical standalone detection (biggest impact)
2. Debug weight quantity extraction  
3. Add DD-Mon-YY date pattern
4. Allow "SPECIAL" as item name
5. Handle leading line numbers in item codes
6. Re-run tests and document final accuracy
