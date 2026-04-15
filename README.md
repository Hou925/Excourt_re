# ExCourt Re — Refactored Campus Court Booking System

A refactored and enhanced version of **[ShanghaineseImpact/ExCourt](https://github.com/ShanghaineseImpact/ExCourt)**.  
This project focuses on software architecture improvement, backend/frontend bug fixes, engineering standardization, and maintainability upgrades.

## Acknowledgement

- Original project: **ShanghaineseImpact/ExCourt**
- Original author: **@ShanghaineseImpact**
- This repository is an independent **refactoring project** based on the original implementation.

## Project Overview

ExCourt is a campus badminton court sharing and booking platform with:
- WeChat Mini Program frontend
- Flask REST API backend
- Relational database storage

Core features include:
- user registration/login
- court exchange / court gifting
- team-up interactions
- friend management
- chat and image messaging
- lost & found

---

## Refactoring Goals

- Improve architecture clarity and extensibility
- Fix critical business and interaction bugs
- Standardize engineering practices
- Enhance API correctness and consistency
- Improve user experience and real-time behavior

---

## Key Improvements

### Architecture
- Migrated **MySQL → PostgreSQL**
- Added Flask **`create_app()` + Blueprints**
- Moved config to **`.env` + python-dotenv**
- Introduced **connection pool + context manager**
- Centralized system path/URL settings

### Design
- Extracted **DAL/Repository** layer
- Standardized **DictCursor** access
- Removed legacy/unused routes

### Features & Bug Fixes
- Rebuilt `/sendphoto` flow (save file → write DB)
- Fixed avatar update + instant refresh
- Implemented real-time chat (text/image)
- Fixed date-switch refresh
- Fixed max-participant update logic
- Moved complex frontend ternary logic to backend
- Fixed court exchange/gifting DB persistence

### Engineering
- Added `.gitignore` and `requirements.txt`
- Centralized backend base URL config
- Added **Marshmallow** request validation
- Unified formatting with **Black + isort**
- Unified API response language to English
- Corrected API semantics (`402→409`, `POST→GET` for `/lost/getall`)
