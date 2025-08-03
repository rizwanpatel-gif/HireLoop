# 🚨 RHero Project Cleanup Plan

## Critical Issues Found:

### 1. **Multiple Backend Main Files** ❌
- `backend/main.py` (✅ CORRECT - keep this)
- `backend/app/main.py` (❌ DELETE - duplicate)
- `backend/app/main_old.py` (❌ DELETE - old version)

### 2. **Duplicate Model Definitions** ❌
- `app/models/models.py` (✅ CANONICAL - keep this)
- `app/routers/candidates.py` has duplicate `CandidateDB` class (❌ REMOVE)
- Various test files with their own models (❌ FIX IMPORTS)

### 3. **Schema Inconsistencies** ❌
- Multiple `CandidateCreate`/`CandidateResponse` definitions
- Empty schemas folder 
- Import conflicts between different files

### 4. **Missing Frontend Implementation** ❌
- All React components are empty
- No API integration

### 5. **Import Chaos** ❌
- Mixed imports from different model files
- Circular dependencies
- Wrong database configurations

## Cleanup Steps:

### Step 1: Remove Duplicate Main Files
- Delete `backend/app/main.py`
- Delete `backend/app/main_old.py`
- Keep only `backend/main.py`

### Step 2: Centralize All Schemas
- Create proper schema files in `app/schemas/`
- Remove duplicate model definitions from routers
- Standardize all imports

### Step 3: Fix Database Configuration
- Remove duplicate database setups in routers
- Use only the centralized `app/core/database.py`

### Step 4: Create Basic Frontend
- Implement CandidateForm component
- Add API service layer
- Create basic candidate submission flow

### Step 5: Standardize Candidate Schema
Based on your requirements: name, email, title, skills, resume_summary, date_to_schedule

## Target Candidate Schema:
```json
{
  "name": "string",
  "email": "string", 
  "current_title": "string",
  "skills": ["string"],
  "resume_summary": "string",
  "preferred_interview_date": "datetime"
}
```

## Action Plan:
1. ✅ Clean up duplicate files
2. ✅ Create centralized schemas  
3. ✅ Fix all imports
4. ✅ Implement basic frontend
5. ✅ Test candidate creation flow
