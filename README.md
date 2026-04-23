
# 🚀 LearnPath AI — Data-Driven Learning Path Recommendation System ![Python](https://img.shields.io/badge/Python-3.13-blue.svg) ![React](https://img.shields.io/badge/React-18.x-61dafb.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)


> **An intelligent, full-stack platform that personalizes learning journeys using hybrid machine learning techniques.**

---

## 🌟 Overview

**LearnPath AI** is an AI-powered educational recommendation system designed to solve a critical problem:

> ❌ *Students don’t know what to learn next.*
> ✅ *This system tells them — intelligently.*

It dynamically generates **structured, personalized learning paths** based on:

* User behavior
* Skill level
* Course interactions
* Similar learners

By combining **Collaborative Filtering + Content-Based Filtering**, the platform ensures **highly relevant, adaptive recommendations** that evolve as the user progresses.

---

## 🧠 Core Intelligence (ML Engine)

### 🔹 Hybrid Recommendation System

A **two-layer recommendation engine**:

1. **User-Based Collaborative Filtering**

   * Finds similar users using interaction patterns
   * Recommends courses liked by similar learners
   * Handles discovery & diversity

2. **Content-Based Filtering**

   * Uses course metadata (tags, difficulty, domain)
   * Matches user profile with course features
   * Ensures relevance & continuity

👉 **Why Hybrid?**
Collaborative filtering alone suffers from *cold start*, while content-based lacks diversity.
This system **balances both** → better accuracy + robustness.

---

## ⚙️ System Architecture

<img width="1254" height="673" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/51489bc0-e64d-4353-894b-df3b69c52e6d" />


---

## ✨ Key Features

### 🎯 Personalized Learning Paths

* Dynamic recommendations based on user progress
* Structured roadmap: Beginner → Intermediate → Advanced

### 📚 Smart Course Catalog

* Domain-based filtering (ML, Web Dev, etc.)
* Difficulty-aware organization
* Tag-based search

### 📊 Progress Analytics Dashboard

* Track completion rates
* Visual progress indicators
* Learning consistency insights

### ⚡ High-Performance Backend

* Built with **FastAPI**
* Async request handling
* Scalable API design

### 🎨 Modern UI/UX

* Glassmorphism-based design
* Smooth animations
* Fully responsive

---

## 🛠️ Tech Stack

### 🔹 Frontend

* React.js (Vite)
* Context API (State Management)
* Responsive CSS (Custom UI)

### 🔹 Backend

* FastAPI (Python)
* SQLite (Lightweight DB)
* Uvicorn (ASGI Server)

### 🔹 Machine Learning

* Pandas, NumPy
* Scikit-Learn
* Similarity Metrics (Cosine Similarity)
* Feature Engineering (Course Tags, Difficulty Encoding)

---

## 🔍 How It Works (Pipeline)

### Step-by-step:

1. Collect user interaction data
2. Build user profile & preferences
3. Compute:

   * User similarity (CF)
   * Feature similarity (Content-based)
4. Merge results using weighted scoring
5. Rank & recommend top courses

---



## 📌 Future Enhancements

* 🔥 Deep Learning-based recommendations (Neural CF)
* 📈 Reinforcement learning for adaptive paths
* 🌐 Deployment (AWS / Vercel / Docker)
* 🧑‍🤝‍🧑 Social learning features
* 🧠 Skill gap analysis

---

## 📊 Impact

✔ Helps students avoid decision paralysis
✔ Encourages structured learning
✔ Improves course completion rates
✔ Adapts to individual learning styles

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork, improve, and submit a PR.

---
## 👨‍💻 Author

**Charan Teja Raipally,Pavan Kumar Bathula**

---

## ⭐ Final Note

This isn’t just a project — it’s a **real-world ML system solving an actual problem in education**.

---


