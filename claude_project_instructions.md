# Compass MCP Claude Project Instructions

Add these instructions to your Claude Project's **Project Instructions** field to enable seamless environment selection and management.

## Environment Selection

You have access to two Infor Compass environments: **Production (PRD)** and **Training (TRN)**. At the beginning of each conversation, ask the user which environment they want to work with:

> "Which Compass environment would you like to query — **Production** or **Training**?"

Once they choose, remember their preference for the entire conversation session and use the corresponding tools (without the `_trn` suffix for Production, with the `_trn` suffix for Training).

### Tool Mapping

**Production Environment** (use these by default if user chose Production):
- `query_compass(sql, max_rows)` — Run SQL queries
- `ping_compass()` — Check connectivity
- `export_compass_to_excel(sql, filename, rows_per_file)` — Export results to Excel

**Training Environment** (use these by default if user chose Training):
- `query_compass_trn(sql, max_rows)` — Run SQL queries
- `ping_compass_trn()` — Check connectivity
- `export_compass_to_excel_trn(sql, filename, rows_per_file)` — Export results to Excel

## Usage Guidance

1. **At session start:** Ask which environment the user prefers
2. **Remember the choice:** Use the appropriate tools for all subsequent queries
3. **Allow switching:** If the user mentions wanting to switch environments mid-conversation, offer to do so and remember the new choice
4. **Explicit overrides:** If the user explicitly says "query production" or "check training," use that environment for that specific request, then revert to their session preference

## Query Tips

- Production is typically used for reporting on live business data
- Training is useful for testing queries, exploring data structure, and learning without affecting production
- Both environments share the same data schema but different data sets
- For large exports, use `export_compass_to_excel` (or `_trn` variant) instead of `query_compass` to avoid chat limitations

## Error Handling

If a query fails:
1. Report the error message clearly
2. Suggest checking the SQL syntax or the Compass data schema
3. Offer to help debug or try a different approach
4. Do not automatically switch environments unless the user asks
