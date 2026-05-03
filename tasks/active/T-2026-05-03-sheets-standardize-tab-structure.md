---
id: T-2026-05-03-sheets-standardize-tab-structure
title: Standardize Google Sheets tab structure across all 5 properties
owner: max
status: open
priority: P2
urgency: nice-to-have
area: automation
waiting_on: Phase 1 completion (current pipeline works for 401/403)
watchers: [rod, devon]
source: 2026-05-03 sheets bridge testing
updated: 2026-05-03
---

## Context

Phase 1 mortgage bridge works on 401/403 Kickapoo (Wells Fargo mortgages). All 5 properties have the same basic sheet structure (Current + Historical sections), but with minor variations:

- **Row number offsets** may differ (Grand Pines, La Estancia, Piney Point)
- **Field labels** vary (different names for escrow, payment, etc.)
- **Servicer types** differ (Wells Fargo vs. New Rez vs. others)
- **Multi-unit handling** unclear (Piney Point Unit B)
- **Grand Pines type** unclear (PM or mortgage?)

Currently, sheets_bridge.py only knows about 401/403. To scale to all properties, need to understand and standardize the others.

## Scope

### Phase 2a: Audit (2-3 hours)
1. Open each property sheet manually
2. Document exact row numbers:
   - Current section start/end
   - Historical section start
   - Year headers and data row counts
3. Document field labels (row-by-row)
4. Clarify Grand Pines type
5. Document multi-unit property handling

### Phase 2b: Standardize (1-2 hours)
1. Decide on standard row numbering (use 401/403 as baseline?)
2. Reorganize sheets to match standard (if needed)
3. Update property_map.json with exact row offsets per property
4. Update sheets_bridge.py to handle all properties

### Phase 2c: Test (1 hour)
1. Verify bridge works on Grand Pines
2. Verify bridge works on La Estancia
3. Verify bridge works on Piney Point

## Issues Found

- 401/403: Standard (rows 9-13 for Current, 18+ for Historical)
- Grand Pines: Field labels differ, type unclear
- La Estancia: Different servicer (New Rez), row offsets unknown
- Piney Point Unit B: Multi-unit property, structure unknown

## Reference

See `/docs/sheets-tab-structure-by-property.md` for detailed comparison matrix and current findings.

## Success Criteria

- [ ] All 5 property sheets audited row-by-row
- [ ] Exact row numbers documented (property_map.json updated)
- [ ] Field labels standardized or variation documented
- [ ] sheets_bridge.py can handle all 5 properties (no special cases)
- [ ] Bridge tested on each property with a real mortgage statement

## Notes

- Not blocking Phase 1 (works for 401/403)
- Low complexity once structure is clear
- Spreadsheet reorganization may be needed (Rod decides)
