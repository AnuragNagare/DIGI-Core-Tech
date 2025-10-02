# Receipt Parser Failure Analysis

## Test Results: 0/11 Passed (0%)

### Critical Issues by Category

#### 1. **Weight-based Quantity Extraction** (Receipt #6: Grocery with Weights)
- **Problem**: Parser defaults to qty=1.0 for all items, ignoring weight information
- **Examples**:
  - `ZUCHINNI GREEN 0.778kg NET @ $5.99/kg` → Extracted qty=1.0, should be 0.778
  - `BANANA CAVENDISH 0.442kg NET @ $2.99/kg` → Extracted qty=1.0, should be 0.442
- **Fix Needed**: Enhanced regex to extract decimal quantities from weight patterns like `0.778kg NET`

#### 2. **Flat Format Parsing Failure** (Receipt #1: Family Restaurant)
- **Problem**: Flat format receipts with tab/space separation not being parsed
- **Example Text**:
  ```
  Item Name         Qty    Rate    Amount
  Pizza Large        1    430.0    430.0
  ```
- **Result**: 0 items extracted
- **Fix Needed**: Improve flat format regex to handle tab-separated columns

#### 3. **Hierarchical Sub-Item Price Inheritance** (Receipts #3, #5, #9, #10)
- **Problem**: Sub-items under group headers inherit parent's price instead of their own
- **Examples**:
  - MVR: `Pizza $103`, `Cookie $12`, `Sandwich $12` all on separate lines → Only `Tea $187` extracted
  - McDonald's: Sub-items under "2 Burritos EVM $6.99" all get price $6.99
  - Cosmopolitan: Items under group all inherit wrong price
- **Fix Needed**: Detect when a line has NO price and is NOT indented → treat as standalone item

#### 4. **Date Extraction** (Receipt #2: Liquor Brand)
- **Problem**: Date format `20-May-18 22:55` not recognized
- **Format**: DD-Mon-YY HH:MM
- **Fix Needed**: Add date pattern for `DD-Mon-YY` format

#### 5. **Total Extraction** (Multiple receipts)
- **Problem**: Totals not being extracted or wrong values
- **Examples**:
  - Family Restaurant: Expected $1060.00, got $0.00
  - Liquor Brand: Expected $1183.60, got $183.60 (missing leading "1")
  - Target: Expected $35.85, got $0.00
- **Fix Needed**: Improve total regex to handle various formats including comma separators

#### 6. **"SPECIAL" Items** (Receipt #6: Grocery)
- **Problem**: Lines with just "SPECIAL $0.99" are being blacklisted
- **Issue**: "SPECIAL" is in blacklist, but these are actual items (discounted products)
- **Fix Needed**: When "SPECIAL" appears with ONLY a price (no other text), treat as item name

#### 7. **Merchant Name Extraction** (Multiple receipts)
- **Problem**: Wrong line being selected as merchant
- **Examples**:
  - McDonald's: Got "KS# 4  08:13:56 AM" instead of "McDonald's"
  - Family Restaurant: Got address line instead of "Family Restaurant"
- **Fix Needed**: Better heuristics for merchant detection (check for brand words, skip timestamps)

#### 8. **Quantity in Item Name** (Receipt #5: McDonald's, Receipt #9: Cosmopolitan)
- **Problem**: Quantity embedded in item name not extracted
- **Examples**:
  - `1 2 Burritos EVM` → qty should be 2, not 1
  - `2 GYRO $50.00` → qty should be 2, extracted as 1
- **Fix Needed**: Parse leading quantity in item names

#### 9. **Item Code Noise** (Receipt #7: Lorem Shop)
- **Problem**: Extra item extracted from "Total" line
- **Example**: `TOTAL $34.50` being extracted as an item
- **Fix Needed**: Strengthen total/subtotal filtering

#### 10. **Multi-line Item Detection** (Receipt #8: Target)
- **Problem**: Items spanning multiple lines not being properly grouped
- **Example**:
  ```
  ELECTRONICS                         1    $12.49 K
  MARIO KART 7 FOR 3DS   T
  ```
- **Fix Needed**: Detect continuation lines (no price on second line)

---

## Fix Priority (High to Low)

1. ✅ **Flat format parsing** (blocks 1 receipt completely)
2. ✅ **Hierarchical standalone items** (affects 4+ receipts)
3. ✅ **Weight-based quantities** (affects grocery receipts)
4. ✅ **Total extraction improvements** (affects half of receipts)
5. ✅ **Date format additions** (minor issue, 1 receipt)
6. ✅ **SPECIAL item handling** (affects 1 receipt)
7. ✅ **Merchant name detection** (cosmetic, affects accuracy checks)
8. ✅ **Embedded quantity extraction** (affects 2 receipts)
9. ✅ **Item code filtering** (minor, 1 extra item)
10. ✅ **Multi-line items** (complex, affects 1 receipt)

---

## Next Steps

1. Start with flat format parsing fix
2. Fix hierarchical standalone items
3. Add weight quantity extraction
4. Improve total extraction
5. Add missing date patterns
6. Re-run tests after each fix to measure progress
