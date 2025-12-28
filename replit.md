# GetHiredAlly - Interview Preparation Application

## Overview
GetHiredAlly is an interview preparation application designed to empower job seekers. It offers advanced job description analysis ("X-Ray"), personalized interview question preparation, and AI-powered answer crafting. The application aims to provide a comprehensive toolkit for users to confidently approach their job interviews, increasing their chances of success.

## User Preferences
I prefer iterative development, with a focus on delivering small, functional increments. Please provide detailed explanations for any complex architectural decisions or significant code changes. I like clean, readable code with a strong emphasis on maintainability. When suggesting changes, please offer multiple options with their respective pros and cons. I want to be asked before any major changes are made to the core logic or database schema.

## System Architecture
The application features a modern web architecture with a React 19 frontend utilizing Vite, Tailwind CSS, and shadcn/ui for a consistent and responsive user experience. The backend is built with FastAPI (Python), providing robust API endpoints and serving the static frontend assets in production. Supabase, a PostgreSQL-based platform, handles data persistence, authentication, and real-time capabilities.

**UI/UX Design:**
- **Color Scheme:** Warm beige (#FAF9F7) background, navy blue (#1E3A5F) primary accents, and dark gray (#333333) text for high readability.
- **Component Library:** Leverages shadcn/ui for consistent, accessible, and themeable UI components.
- **Workflow:** Emphasizes a coaching-style language, especially in AI interactions, focusing on "Focus Areas" instead of "weaknesses" to foster a positive user experience.

**Technical Implementations:**
- **Authentication:** User registration and login utilize bcrypt for password hashing and Supabase for session management. Email verification is implemented via the Resend API.
- **AI Integration:** A unified AI service routes requests to Claude or Gemini models via LiteLLM, allowing users to select their preferred provider. All AI interactions are logged for usage tracking, cost analysis, and auditing.
- **Interview Questions:** A comprehensive database of 54 static interview questions categorized into Universal, Behavioral, Situational, Self-Assessment, and Cultural Fit, each with detailed preparation guidance. Dynamic, AI-generated questions are personalized based on user input.
- **CV Optimization:** An AI-powered CV optimizer scans resumes (PDF, DOCX, TXT), identifies issues, suggests improvements, and can even generate a fixed version with side-by-side comparison. CV content is encrypted at rest using Fernet.

**Feature Specifications:**
- **Job Description X-Ray:** Analyzes job descriptions using AI to extract key requirements and suggest relevant interview preparation.
- **Interview Question Predictor:** Provides access to static questions with varying levels of detail (questions only, with tips, full prep) and generates smart, personalized questions.
- **CV Optimizer:** Scans CVs, identifies strengths and areas for improvement, and offers AI-generated fixes.
- **User Tiers:** Differentiated access and usage limits based on user profiles (Standard, Special, VIP) for various services.

**System Design Choices:**
- **Security:** Implements security headers, rate limiting on sensitive endpoints, audit logging for security events, input validation with Pydantic, and secure password handling.
- **Scalability:** Utilizes Supabase for a managed and scalable database solution, and FastAPI for an asynchronous and high-performance backend.
- **Environment Variables:** Critical configurations are managed via environment variables for secure deployment.

## External Dependencies
- **Supabase:** Database (PostgreSQL), Authentication, Storage.
- **Vite:** Frontend build tool.
- **Tailwind CSS:** Utility-first CSS framework.
- **React Router:** Frontend routing.
- **Resend API:** Email sending for verification.
- **Claude AI (Anthropic):** Job description analysis.
- **Gemini AI (Google):** Personalized interview question generation, CV analysis.
- **LiteLLM:** Unified interface for various LLM providers, including cost tracking.