# /reading-review

**Purpose**: Session-starting command to enforce mandatory research readings at development phase transitions, ensuring industry-grade implementation.

## Command Usage

```
/reading-review
```

Run at the start of every development session. When invoked, Claude Code will:
1. Identify current development phase
2. Enforce mandatory readings for that phase
3. Verify understanding before allowing code development
4. Handle research gaps with ChatGPT integration

---

## Command Implementation

You are Claude Code, helping with the EV Battery Health Monitor project. When `/reading-review` is invoked at session start, you MUST follow this protocol:

### Step 1: Phase Identification

Check current development phase by examining:
- Current git branch name
- CLAUDE.md roadmap status  
- Recent commits and file changes
- Active development directory

### Step 2: Mandatory Reading Enforcement

Based on identified phase, ENFORCE these mandatory readings:

#### Phase 1: Data Simulation Engine
**MANDATORY READINGS** 🔴:
- Section 5: "Realistic Data Simulation" (EV discharge patterns, CC-CV charging, voltage/current ranges)
- Section 1: "Key Metrics Tracked" (standard units, SoH calculation, sampling rates)
- Section 5: "Anomalies to Include" (thermal events, capacity fade, sensor glitches)

#### Phase 2: Database & Backend Setup
**MANDATORY READINGS** 🔴:
- Section 3: "Architecture Best Practices - Data Modeling & Partitioning"
- Section 3: "Continuous Aggregations & Downsampling"  
- Section 5: "WSL2 + Docker Workflow Best Practices"

#### Phase 3: Backend API Development
**MANDATORY READINGS** 🔴:
- Section 1: "Industry Protocols and APIs"
- Section 3: "Real-Time vs Batch in UI"

#### Phase 4: Frontend & Visualization
**MANDATORY READINGS** 🔴:
- Section 5: "Visualization Standards in Automotive Dashboards"
- Section 5: "Annotation/Labeling UI" 
- Section 1: "Sampling Rates & Data Volume"

#### Phase 5: Advanced Features & Polish
**MANDATORY READINGS** 🔴:
- Section 5: "Features to Stand Out to Employers"
- Section 6: "Future-Proofing and Emerging Trends"

### Step 3: Reading Verification Protocol

Before allowing ANY code development:

1. **STOP all coding activities immediately**
2. **Present mandatory readings list** with specific sections
3. **Ask for explicit confirmation**: "Have you read all the mandatory sections listed above?"
4. **Conduct understanding quiz**:
   - Ask 2-3 specific questions from the readings
   - Require detailed answers demonstrating comprehension
   - Examples: "What is the CC-CV charging profile?", "What voltage ranges are realistic for EV batteries?"
5. **Only proceed after satisfactory demonstration** of understanding

### Step 4: Research Gap Detection

If no relevant research exists for current phase:

1. **IMMEDIATELY STOP development**
2. **Identify specific research gaps** (e.g., "No research found for WebSocket real-time data streaming patterns in automotive telemetry")
3. **Present research options**:

```
🔴 RESEARCH GAP DETECTED

Missing research for: [specific technical topic]
Current phase: [development phase]
Impact: Cannot proceed with industry-grade implementation

Options:
A) Generate ChatGPT research request for deep technical analysis
B) Find and review industry sources manually  
C) Proceed with basic implementation (NOT RECOMMENDED - may result in non-industry-standard code)

Which approach would you prefer?
```

### Step 5: ChatGPT Research Integration

If user selects ChatGPT research option, generate this formatted request:

```
=== ChatGPT Research Request ===

PROJECT CONTEXT:
- Project: EV Battery Health Monitor
- Tech Stack: React/Next.js, FastAPI, PostgreSQL/TimescaleDB, Docker
- Current Phase: [specific phase]
- Gap: [specific research need]

RESEARCH TOPIC: [specific technical area needing research]

RESEARCH REQUIREMENTS:
Please provide comprehensive analysis covering:

1. **Industry Best Practices**
   - Current standards in automotive/EV industry
   - Regulatory compliance considerations
   - Performance benchmarks

2. **Technical Implementation Patterns**
   - Proven architectural approaches
   - Code patterns and examples
   - Integration strategies with our tech stack

3. **Common Pitfalls & Anti-Patterns**
   - What to avoid in implementation
   - Known failure modes
   - Debugging strategies

4. **Performance & Scalability**
   - Performance optimization techniques
   - Scalability considerations
   - Resource usage patterns

5. **Security Implications**
   - Security best practices
   - Vulnerability prevention
   - Data protection strategies

TARGET LEVEL: Senior developer / architect level
OUTPUT FORMAT: Structured technical guide with actionable insights
FOCUS: Production-ready, industry-grade implementation
```

### Step 6: Research Integration Workflow

After receiving ChatGPT research:

1. **Update project documentation**:
   - Add new research section to relevant file
   - Update CLAUDE.md with new mandatory readings
   - Create phase-specific implementation notes

2. **Create new checkpoint**:
   - Add the new research to mandatory readings
   - Re-run `/reading-review` to enforce new requirements

3. **Document research application**:
   - Note how research will be applied in implementation
   - Update development task list with research-informed approaches

### Step 7: Session Workflow Integration

**Start of Every Session**:
1. User runs `/reading-review`
2. Claude identifies current phase and mandatory readings
3. Claude verifies user has completed readings
4. Claude quizzes understanding of key concepts
5. Only after verification, Claude allows development to proceed
6. If research gaps found, Claude stops and requests research

**Enforcement Rules**:
- ❌ NEVER skip research verification process
- ❌ NEVER accept "I'll read it later" or similar deferrals
- ❌ NEVER allow coding without confirmed understanding
- ✅ ALWAYS update CLAUDE.md with reading confirmations
- ✅ ALWAYS adapt to project evolution with new research needs
- ✅ ALWAYS prioritize industry-grade implementation over speed

---

## Project Adaptation Guide

To adapt this command for future projects:

### 1. Update Research Sources
Replace references to:
- "Industry Standards Research" document with new project research
- Specific section numbers with new research structure
- Technical focus areas with new domain expertise

### 2. Modify Phase Structure
Adapt the phase breakdown to match new project roadmap:
- Change phase names and descriptions
- Update mandatory reading requirements per phase
- Adjust technical focus areas for new domain

### 3. Customize Verification Questions  
Create project-specific quiz questions:
- Technical concepts relevant to new domain
- Industry standards for new field
- Implementation patterns for new tech stack

### 4. Update ChatGPT Request Template
Modify the research request template:
- Change project context and tech stack
- Adjust research focus areas
- Update target expertise level if needed

---

## Usage Pattern

**Every Session Start**:
```bash
# User starts development session
# First command should always be:
/reading-review

# Claude then enforces current phase readings
# Only after verification can development proceed
```

This ensures every development session begins with proper research foundation, parallel to your `/md-review` workflow for codebase awareness.