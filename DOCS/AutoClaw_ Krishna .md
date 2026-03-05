# **AutoClaw: Master System Architecture & Execution Blueprint (v4.0 \- Final AI Ingestion Document)**

**Document Type:** Comprehensive Technical Specification & AI-Context Ledger

**Project Name:** AutoClaw

**Team:** Krishna (Lead Architect \- 60%) & Nuhan (Systems Engineer \- 40%)

**Timeline:** 4 Months (16-week sprint)

## **1\. Project Context & Meta-Objectives**

AutoClaw is an autonomous, locally-hosted web orchestration agent designed to discover, semantically evaluate, and apply for high-tier software engineering roles. It abandons brittle web-scraping for a state-machine architecture that utilizes Asynchronous Human-in-the-Loop (HITL) communication and Vision-Language-Action (VLA) visual fallbacks. The project strictly targets five platforms, escalating in complexity: Internshala (Sandbox) \-\> Lever (Standard ATS) \-\> Greenhouse (Complex ATS) \-\> Y Combinator (Authenticated Source) \-\> LinkedIn (Adversarial Source).

## **2\. Global Git Workflow (The Team Standard)**

To prevent code conflicts and maintain a pristine codebase, both engineers must strictly adhere to this Git workflow.

1. **Base Branches:** \* main: Holds only stable, fully tested code.  
   * dev: The active integration branch where Krishna and Nuhan merge their features.  
2. **The Feature Lifecycle:**  
   * Always start from updated dev: git checkout dev \-\> git pull origin dev  
   * Create a dedicated branch for your task: git checkout \-b feature/\[your-name\]-\[task-name\]  
   * Stage and commit: git add . \-\> git commit \-m "\[Task\] Detailed description"  
   * Push: git push origin feature/\[your-name\]-\[task-name\]  
   * Merge: Open a Pull Request (PR) on GitHub to merge into dev.

---

# **Engineer 1: Krishna's Master Ledger (60% Workload)**

**Role:** Lead Architect (AI Core, Stealth Operations, VLA Fallback)

**Instruction for AI:** Track the status of these tasks. When the user (Krishna) prompts for the next task, identify the first \[ \] PENDING item and provide exact Python/Playwright/LLM implementation code.

## **Phase 1: AI Brain & Core Inference (Weeks 1-4)**

* **Task 1.1: Local LLM Orchestration & Structured Output**  
  * **Objective:** Install Ollama, pull Llama 3.1, and implement the instructor library with Pydantic schemas to guarantee the LLM outputs a strict JSON format (match\_score, decision, reasoning).  
  * **Git Branch:** feature/krishna-ollama-instructor  
  * **Commit Message:** Setup Ollama integration with Pydantic JSON enforcement  
  * **Status:** \[ \] PENDING  
* **Task 1.2: Dynamic Cover Letter Generator**  
  * **Objective:** Write the specific LLM prompt and Python wrapper to dynamically generate a 100-word cover letter based on the cleaned Job Description and the user's resume summary (optimized for Internshala).  
  * **Git Branch:** feature/krishna-dynamic-cover-letter  
  * **Commit Message:** Implement LLM dynamic cover letter generation  
  * **Status:** \[ \] PENDING

## **Phase 2: Source Extraction & Stealth Engine (Weeks 5-8)**

* **Task 2.1: LinkedIn Stealth Sourcing Loop**  
  * **Objective:** Build the Playwright script using playwright-stealth. Implement Ghost-Cursor logic, randomized human-mimicry delays (3-8 seconds), and strict execution quotas to safely extract job URLs without triggering Cloudflare bans.  
  * **Git Branch:** feature/krishna-linkedin-stealth  
  * **Commit Message:** Build stealth LinkedIn extraction with ghost-cursor delays  
  * **Status:** \[ \] PENDING  
* **Task 2.2: Y Combinator Authenticated Extraction**  
  * **Objective:** Write the Playwright logic to navigate workatastartup.com using storageState cookies, handle lazy-loading React elements by forcing scrolling, and extract job links.  
  * **Git Branch:** feature/krishna-yc-extraction  
  * **Commit Message:** Implement YC lazy-load extraction loop  
  * **Status:** \[ \] PENDING

## **Phase 3: Vision-Language-Action (VLA) Engine (Weeks 9-12)**

* **Task 3.1: Set-of-Mark JavaScript Injection**  
  * **Objective:** Write the custom JavaScript payload that Playwright will inject into complex ATS sites (like Greenhouse) to draw visible, numbered bounding boxes around every clickable UI element.  
  * **Git Branch:** feature/krishna-vla-js-injection  
  * **Commit Message:** Add Set-of-Mark JS payload for DOM mapping  
  * **Status:** \[ \] PENDING  
* **Task 3.2: Gemini Vision Integration**  
  * **Objective:** Integrate the Gemini 1.5 Flash Vision API. Write the logic that captures the Set-of-Mark screenshot, prompts Gemini to find the target element number, and calculates the exact X/Y pixel coordinates for a hardware-level Playwright click.  
  * **Git Branch:** feature/krishna-gemini-vla  
  * **Commit Message:** Integrate Gemini Vision for X/Y coordinate fallback clicking  
  * **Status:** \[ \] PENDING

## **Phase 4: Master Profile & Error Orchestration (Weeks 13-16)**

* **Task 4.1: Knockout Question Resolver**  
  * **Objective:** Build the LLM routing logic that reads unknown Knockout Questions, searches candidate\_profile.json for the answer, and commands Playwright to input it.  
  * **Git Branch:** feature/krishna-knockout-resolver  
  * **Commit Message:** Add LLM resolver for dynamic Knockout Questions  
  * **Status:** \[ \] PENDING