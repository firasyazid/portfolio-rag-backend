# Projects Portfolio

This document showcases Firas Yazid's personal projects, freelance work, and experimental applications that demonstrate his expertise in AI, full-stack development, and DevOps.

---

## AI & Machine Learning Projects

### Smart CI/CD Pipeline with AI-Powered MCP Release Gate
**Duration:** January 2026  
**GitHub:** https://github.com/firasyazid/AI-release-Manager--MCP-

#### Project Overview
Firas Yazid built an AI-powered CI/CD release gate using MCP architecture to intelligently control deployments. The system analyzes test results, code quality, coverage, and security metrics using Google Gemini AI, assigns confidence scores, and automatically approves or blocks releases.

#### Key Features
- **AI-Powered Analysis:** Evaluates tests, coverage, linting, and security metrics using Google Gemini AI
- **Intelligent Decision Making:** Understands why a build may be risky and assigns confidence scores
- **Automated Deployment Control:** Generates decisions to APPROVE or BLOCK deployment
- **Comprehensive Reporting:** Produces release summaries in JSON or Markdown format, detailing what passed, what failed, and why
- **GitHub Actions Integration:** Runs unit tests, linting, type checks, and coverage reports on every push
- **Docker Support:** Builds Docker images for applications
- **Production Deployment:** Automatically deploys to production when approved

#### Key Benefits
- Intelligent decisions based on context, not just thresholds
- Zero-failure deployments by blocking unsafe builds automatically
- Project-agnostic design that can plug into any CI/CD pipeline
- Auto-generated release summaries and AI explanations for debugging
- Production-ready integration with GitHub Actions, GitLab CI, Jenkins, and Docker

#### Technologies Used
Python, MCP (Model Context Protocol), Google Gemini AI, GitHub Actions, Docker, CI/CD

---

### Applied Machine Learning: Face Verification & Liveness Detection
**Duration:** December 2025  
**GitHub:** https://github.com/firasyazid/Face-Verification-Liveness-Detection-system

#### Project Overview
Firas Yazid implemented a secure face-based user onboarding pipeline combining face verification and active liveness detection to prevent identity fraud such as photo attacks, screen replays, or prerecorded videos.

#### System Architecture

**Face Verification:**
- Face embeddings extracted using FaceNet512 via DeepFace
- Identity matching performed using cosine similarity between enrolled profile image and live capture
- Threshold-based decisioning ensures robustness against false positives

**Liveness Detection (Anti-Spoofing):**
- Real-time facial landmark extraction using MediaPipe Face Mesh
- Head pose estimation with challenge-response logic (yaw, pitch, roll variations)
- Detects static images and replay attacks by validating natural 3D face movement
- Temporal consistency validation

#### Technical Stack
- **Backend:** FastAPI (Python) for video frame processing, face embedding extraction, comparison, and liveness decision engine
- **Computer Vision:** OpenCV for frame handling and preprocessing, MediaPipe for facial landmarks
- **Mobile Frontend:** Expo (React Native) for profile image capture and live video streaming

#### Technologies Used
Python, FastAPI, Machine Learning, React Native, OpenCV, MediaPipe, DeepFace, FaceNet512

---

### AI-Powered Interactive Journaling with RAG
**Duration:** October 2025

#### Project Overview
Firas Yazid built a personal journaling application that allows users to interact with their past entries using advanced AI techniques. Each journal entry is converted into embeddings and stored in a vector database for semantic search.

#### Key Features
- **Semantic Search:** Journal entries converted into embeddings using text-embedding-bge-m3
- **Vector Storage:** Stored in Pinecone for efficient similarity search
- **Context-Aware Responses:** LangChain retrieves relevant entries and provides intelligent responses via Qwen model
- **Interactive Experience:** Users can ask questions about their past entries and receive personalized insights
- **Full-Stack Solution:** Complete mobile application with backend API

#### Technologies Used
React Native (Expo), NestJS, MongoDB, LangChain, LM Studio, Pinecone, Qwen LLM, Vector Embeddings

---

### Full-Stack AI Assistant: Web Scraping + RAG + LLM
**Duration:** August 2025 - September 2025  
**Demo:** Available

#### Project Overview
Firas Yazid developed a RAG agent for web scraping and question answering, enabling users to scrape any website, store content intelligently, and ask natural language questions to receive contextual AI-powered answers.

#### Key Features
- **Web Scraping:** Powered by LangChain WebBaseLoader for extracting content from any URL
- **Smart Processing:** Content split and stored in ChromaDB with embeddings
- **Natural Language Queries:** Ask questions in plain language and get contextual answers from LLM
- **Modern UI:** Interactive React frontend with TailwindCSS
- **RESTful API:** Built with FastAPI for seamless integration
- **End-to-End Pipeline:** Complete flow from scraping to chunking, storage, retrieval, and AI answers

#### Technical Highlights
- Hybrid embeddings for better semantic search
- Persistent vector storage with ChromaDB
- LangGraph pipeline orchestration
- OpenAI's text-embedding-ada-002 for embeddings

#### Technologies Used
React, TailwindCSS, FastAPI, LangChain, ChromaDB, OpenAI Embeddings, LangGraph, RAG Architecture

---

### AI Data Insights Agent
**Duration:** August 2025  
**Demo Video:** Available

#### Project Overview
Firas Yazid created a revolutionary AI agent that transforms database interactions into natural conversations. The system connects to databases in real-time, understands natural language instructions, and delivers clear insights through a clean React interface.

#### Key Features
- **Natural Language Database Queries:** Users ask questions in plain language instead of writing complex SQL
- **Real-Time Connectivity:** Connects to databases in real-time
- **Intelligent Reasoning:** Searches and reasons through data intelligently
- **Clear Insights:** Delivers actionable insights via React interface
- **User-Friendly:** Eliminates the need for SQL knowledge

#### Technologies Used
Python (Agno), Qwen LLM (via LM Studio), React, Database Connectivity

---

### AI-Powered GitHub Assistant with MCP + Llama
**Duration:** August 2025  
**GitHub:** https://github.com/firasyazid/AI-Powered-GitHub-Assistant-with-MCP  
**Demo Video:** Available

#### Project Overview
Firas Yazid built a GitHub AI Assistant that integrates directly with repositories to make issue handling and code review smarter, exploring the intersection of AI and developer tools.

#### Key Features

**AI-Powered Code Review:**
- Select any file from repository for analysis
- Analyzes code for potential bugs, missing documentation, and untested logic
- Suggests improvements for readability, maintainability, and best practices
- Works offline with Llama running locally on LM Studio

**Issue Triage:**
- Fetches all repository issues in real-time
- Summarizes issue descriptions into short, actionable overviews
- Auto-suggests labels (bug, enhancement, documentation) to save maintainers time

#### Technologies Used
Llama LLM (via LM Studio), MCP (Model Context Protocol), Node.js, GitHub REST API, React, Tailwind CSS

---

### AI-Powered Gym Assistant App with MCP
**Duration:** May 2025  
**GitHub:** https://github.com/firasyazid/AI-Powered-Fitness-app-with-MCP  
**Demo Video:** Available

#### Project Overview
Firas Yazid developed a fitness application powered by AI that not only generates personalized workout plans but remembers and understands the user over time. This project explores the practical use of Model Context Protocol (MCP) with locally hosted LLaMA 3 model.

#### Key Features
- **MCP Integration:** AI prompts enriched with personal context including past workouts, injuries, and emotional states
- **AI-Powered Coaching:** Real, adaptive fitness support beyond simple content generation
- **Personalized Plans:** Context-aware workout recommendations based on user history
- **Memory System:** Remembers user preferences, limitations, and progress over time

#### Technical Stack
- **LLM:** LLaMA 3 (local, via LM Studio)
- **Backend:** FastAPI with MongoDB
- **Frontend:** React Native (Expo SDK 53)
- **Authentication:** Secure JWT with AsyncStorage
- **UX/UI:** Minimalist dark theme for focused user experience

#### Why It Matters
Demonstrates how LLMs and MCP can transform from simple prompts into real-world applications that adapt like a human coach, showing what's possible when memory meets motivation.

#### Technologies Used
LLaMA 3, MCP, FastAPI, MongoDB, React Native, Expo, JWT Authentication

---

## Mobile Applications (Published)

### EVA Padel – Real-Time Paddle Tournament & Player Tracking
**Duration:** January 2025 - March 2025  
**Platform:** Available on App Store  
**Link:** https://apps.apple.com/tn/app/eva-padel/id6757681607

#### Project Overview
Firas Yazid developed a comprehensive application dedicated to paddle players, coaches, and clubs. The app streamlines tournament and match management while providing performance tracking for players.

#### Key Features
- **Match & Tournament Management:** Create and manage matches and tournaments
- **Player Evaluation:** Coaches can add reviews and feedback for each player
- **Player Level Calculation:** Automatic calculation of each player's level based on performance
- **Live Tournament Support:** Real-time scores, ratings, and updates during tournaments
- **Personalized Dashboards:** Separate dashboards for players and coaches
- **Live Notifications:** Updates and notifications during tournaments

#### Technologies Used
React Native, Node.js, Express.js, MongoDB, Java, Docker, CI/CD Pipeline

---

### Pilate & Co - Cross-Platform Mobile Application
**Duration:** January 2025 - February 2025  
**Platform:** Available on App Store  
**Link:** https://apps.apple.com/app/pilates-co

#### Project Overview
Firas Yazid built a modern, high-performance mobile application for Pilates enthusiasts designed to deliver a seamless and engaging user experience.

#### Key Features
- **Secure Authentication:** User login and registration system
- **Online Class Reservations:** Book Pilates classes directly through the app
- **Subscription Management:** Manage memberships and subscriptions
- **Social News Feed:** Real-time interactions to foster community engagement
- **Multilingual Support:** French and English for global audience reach
- **Push Notifications:** Expo push notifications to remind users of upcoming sessions
- **Online Payment Integration:** Integrated payment system (coming soon)
- **Intuitive Interface:** High-performance, user-friendly design

#### Technologies Used
React Native, React.js, Node.js, MongoDB, Expo Push Notifications

---

## Web Applications

### E-commerce Platform with Next.js
**Duration:** October 2024 - December 2024  
**Associated With:** Parhelion Consulting & Training  
**Demo:** https://e-comm-app-next-js-8c99.vercel.app/

#### Project Overview
Firas Yazid developed a modern e-commerce platform using Next.js and Wix Headless for a high-tech devices shop. The platform demonstrates flexibility and can be easily adapted to various industries.

#### Key Highlights
- **Modern Architecture:** Wix Headless chosen for cost-effective, streamlined content management
- **High Performance:** Personalized, high-performance user experiences
- **Flexibility:** Easily adaptable to different industries
- **Official Launch:** Set for early 2025
- **Responsive Design:** Optimized for all devices

#### Technologies Used
Next.js, Wix Headless CMS, Tailwind CSS, Vercel Deployment

---

### EMSAT Exam Simulation Platform
**Duration:** July 2024 - October 2024

#### Project Overview
Firas Yazid developed a full-stack web application for an apprenticeship agency in Dubai to simulate the EMSAT test, providing students with a comprehensive practice platform.

#### Key Features
- **Real-Time Test Simulation:** Authentic EMSAT exam experience
- **Dynamic Question Types:** Single choice, multiple choice, and drag-and-drop questions
- **Progress Tracking:** Students can track their performance and improvement
- **Result Analysis:** Detailed analytics on test results
- **Student Dashboard:** User-friendly interface for practicing exams and viewing results
- **Fully Responsive Design:** Accessible on all devices
- **Containerized Deployment:** Docker for scalability and efficiency

#### Technologies Used
Angular, Node.js, MongoDB, PostgreSQL, Docker

---

### Machine Learning Disease Prediction Platform
**Duration:** May 2024 - July 2024  
**Associated With:** B2M-IT

#### Project Overview
Firas Yazid developed a web application utilizing five supervised machine learning models to predict diseases based on symptoms, including COVID-19, heart disease, diabetes, breast cancer, and 50 other illnesses.

#### Key Features
- **Multiple Disease Prediction:** Five specialized ML models for different disease categories
- **Symptom-Based Analysis:** Predict diseases based on user-reported symptoms
- **High Accuracy:** Models trained and optimized for reliable predictions
- **Web Interface:** User-friendly web application for healthcare specialists
- **Real-Time Predictions:** Instant disease prediction results

#### Technologies Used
Python, Machine Learning, Flask, Scikit-learn

#### Related Achievement
Achieved **98.07% accuracy** and **98.13% precision** with RandomForestClassifier for COVID-19 prediction model.

---

## DevOps & Infrastructure Projects

### CI/CD Pipeline with GitLab
**Duration:** June 2024  
**Associated With:** B2M-IT

#### Project Overview
Firas Yazid successfully built and implemented a robust CI/CD pipeline for the Intelligent Health Application using GitLab, fully deployed in the cloud.

#### Pipeline Stages
1. **Monitoring:** Ensures system health is always in check
2. **Artifact Construction:** Compiles code and prepares build artifacts
3. **SonarCloud Check:** Runs static code analysis for code quality and security
4. **Testing:** Executes unit tests to validate functionality
5. **Build:** Constructs the final build for deployment
6. **Deployment:** Automatically deploys application to target environment

#### Key Challenge
Building the entire pipeline 100% in the cloud was a significant achievement, enabling faster delivery times, improved code quality, and enhanced team collaboration.

#### Technologies Used
GitLab CI/CD, Docker, SonarCloud, DevOps Best Practices, Cloud Deployment

---

### DevOps CI/CD Pipeline Project
**Duration:** December 2023  
**Associated With:** ESPRIT  
**GitHub:** https://github.com/firasyazid/Devops_project

#### Project Overview
Firas Yazid led the implementation of a comprehensive DevOps pipeline for a Spring Boot and Angular application, demonstrating deep understanding of DevOps tools and practices.

#### Key Implementations
- **Continuous Integration:** Smooth CI with Jenkins Pipelines
- **Application Management:** Agile management of Spring Boot and Angular applications
- **Code Quality Monitoring:** Constant monitoring with SonarQube
- **Containerization:** Orchestrated working environment with Docker Compose
- **Continuous Delivery:** Seamless CD with DockerHub

#### Technologies Used
Jenkins, Docker, Docker Compose, Spring Boot, Angular, SonarQube, Nexus, DockerHub

---

## Early Projects & Learning Journey

### Mobile Car Rental Application
**Duration:** November 2023 - January 2024  
**Associated With:** Parhelion Consulting & Training  
**GitHub:** https://github.com/firasyazid/Car_Rent_App

#### Project Overview
Firas Yazid developed a mobile car rental application allowing users to search, book, and manage car rentals in real-time.

#### Key Features
- Real-time car booking and management
- Geolocation features for finding nearby cars
- Push notifications for booking updates
- Intuitive user interface for optimal user experience

#### Technologies Used
React Native, Node.js, Express.js, Docker

---

### Mobile Service Application "Ilo9"
**Duration:** January 2023 - April 2023  
**Associated With:** Parhelion Consulting & Training  
**GitHub:** https://github.com/firasyazid/-Mobile-Project-nodejs

#### Project Overview
Firas Yazid developed a mobile service application to connect users with service providers for tasks such as housekeeping, gardening, and other domestic work.

#### Key Features
- Service provider search functionality
- Multiple task categories (housekeeping, gardening, etc.)
- Secure payment integration
- Dashboard for managing services, providers, and users
- Accessible and user-friendly design

#### Technologies Used
React Native, MongoDB, Node.js, Angular, Docker

---

### Delta Architect Mobile Application
**Duration:** June 2023 - September 2023  
**Associated With:** Parhelion Consulting & Training  
**Platform:** Published on Google Play  
**Link:** https://play.google.com/store/apps/details?id=com.deltaarchitecte

#### Project Overview
Firas Yazid developed a mobile application for Delta Cuisine architects to manage their orders, track commands, stay updated with news, and access a loyalty system.

#### Key Features
- Order and command management system
- News updates feed
- Loyalty program integration
- Built with React Native and Node.js for seamless user experience

#### Technologies Used
React Native, Node.js, MongoDB, Angular, Expo, Express.js, Docker

---

### 3D E-commerce App Prototype
**Duration:** March 2024

#### Project Overview
Firas Yazid created an innovative e-commerce app prototype incorporating 3D model animations to provide users with an interactive shopping experience.

#### Key Features
- Interactive 3D product models
- Rotate and zoom functionality for detailed product visualization
- Realistic and detailed visualizations enhancing online shopping
- Enhanced user engagement through immersive 3D experiences

#### Technologies Used
React Native, Three.js

---

### E-Portfolio Website
**Duration:** March 2024  
**Website:** https://firasyazid.github.io/e-portfolio/

#### Project Overview
Firas Yazid developed a personal e-portfolio to showcase his journey as a Full-Stack Software Engineer, providing a comprehensive overview of skills, projects, and professional experiences.

#### Features
- Project showcase with descriptions and technologies
- Skills and competencies display
- Professional experience timeline
- Contact information and social links
- Modern, responsive design

#### Technologies Used
Modern web technologies, GitHub Pages deployment

---

## Academic & Learning Projects

### Loan Approval Prediction Model
**Duration:** November 2023

#### Project Overview
Firas Yazid developed a comprehensive Loan Approval Prediction System utilizing both Logistic Regression and Neural Network models to enhance prediction accuracy for financial institutions.

#### Key Achievements
- **Logistic Regression Model:** Achieved 81% training accuracy
- **Neural Network Model:** Achieved 78.86% accuracy using Keras
- Extensive training and optimization for both models
- Comparison of traditional ML vs. deep learning approaches

#### Technologies Used
Python, Machine Learning, Scikit-learn, Keras, Neural Networks

---

### News App with React Native
**Duration:** October 2022 - November 2022  
**GitHub:** https://github.com/firasyazid/NewsApp_React_Native

#### Project Overview
A lightweight application for browsing the latest news articles seamlessly, powered by the NewsData.io API. Developed during Firas Yazid's journey of mastering React Native.

#### Technologies Used
React Native, Expo, NewsData.io API

---

### Movie Navigation Application
**Duration:** September 2022 - October 2022  
**GitHub:** https://github.com/firasyazid/Forja_app_react_native

#### Project Overview
Firas Yazid developed a mobile application with React Native allowing users to navigate and discover various movies in an intuitive and interactive way during his React Native learning journey.

#### Technologies Used
React Native, Node.js

---

### Film Web Application
**Duration:** August 2021 - September 2021

#### Project Overview
Firas Yazid built a responsive web application with React.js for exploring a vast collection of movies.

#### Key Features
- Movie navigation by categories (popular, top-rated, upcoming)
- Search functionality by movie title
- Detailed movie information (synopsis, release date, cast, ratings)
- User authentication for personalized features
- Favorites list management for registered users
- Responsive design for all devices

#### Technologies Used
React.js, Node.js

---

### E-commerce Web Application (MEAN Stack)
**Duration:** July 2022 - September 2022  
**Associated With:** Parhelion Consulting & Training  
**GitHub:** https://github.com/firasyazid/AngularProject

#### Project Overview
Firas Yazid developed a complete e-commerce platform using the MEAN stack with smooth, responsive user