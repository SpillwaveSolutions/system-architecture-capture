# PRD — System Architecture Capture

## Problem

Modern systems span microservices, IaC, CI/CD, IAM, networking, SSO, and tickets/wikis. Knowledge is scattered; agents cannot answer blast-radius or dependency questions with precision.

## Goal

Build an indexed **second brain** over one monorepo or many repos for **project information**, using a **standard set of OKF schemas** (OKF core + PKC + SAC architecture types): services, infra, pipelines, identity, ownership, and relationships an LLM can reason over accurately.

## Solution

SAC reverse-engineers repos (+ optional wiki/tickets) into a structured OKF knowledge graph extending PKC.

## Users

- Platform engineers onboarding to a system
- Agents performing change-impact analysis
- Architects maintaining living ADRs and topology maps

## Success

- Point at repos → knowledge bundle with services, packages, infra, pipelines, identity
- Query via pack/search with typed edges
- Works as Claude / Grok / Codex / OpenCode plugin
