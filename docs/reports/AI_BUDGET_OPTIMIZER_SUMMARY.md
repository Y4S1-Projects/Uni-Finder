# AI-Powered Student Budget Optimizer

## DECLARATION
This document presents the Student Budget Optimizer component developed as part of the Uni-Finder platform. The work focuses on helping Sri Lankan university students estimate monthly expenses, identify financial risk, and receive AI-assisted budget optimization guidance.

## ABSTRACT
The Student Budget Optimizer is an AI-enabled financial planning component designed to support university students in managing their monthly living costs. The solution combines rule-based cost calculation, Sri Lanka-specific reference datasets, machine learning-based budget prediction, risk classification, and AI-generated optimization strategies. The component collects academic, financial, food, transport, and additional expense inputs from the user and generates a complete analysis including estimated food and transport costs, total monthly expenses, projected savings, financial risk level, and personalized recommendations. The system is implemented using a React frontend, a Flask microservice for budget analysis, and an Express backend for persistence. It is tailored to local student life by incorporating Sri Lankan districts, transportation patterns, rental data, and food cost behavior. The component aims to improve student financial awareness, support more realistic spending plans, and provide actionable guidance for reducing unnecessary expenses.

## ACKNOWLEDGEMENT
This component was developed as part of the Uni-Finder research implementation. Appreciation is extended to the project supervisors, team members, dataset contributors, and student users whose requirements helped shape the design of the budget optimization workflow.

## TABLE OF CONTENT
1. Declaration
2. Abstract
3. Acknowledgement
4. Table of Content
5. List of Figures
6. List of Tables
7. List of Abbreviations
8. Introduction
9. Methodology
10. Results and Discussion
11. Conclusion

## LIST OF FIGURES
- Figure 1: Overall architecture of the Student Budget Optimizer
- Figure 2: User workflow of the multi-step budget form
- Figure 3: Complete analysis response flow
- Figure 4: AI-powered optimization strategy generation flow
- Figure 5: Results dashboard and final budget transformation view

## LIST OF TABLES
- Table 1: Functional requirements of the Student Budget Optimizer
- Table 2: Non-functional requirements
- Table 3: Core datasets used by the component
- Table 4: Input and output structure of the analysis service
- Table 5: Summary of generated result sections

## LIST OF ABBREVIATIONS
- AI: Artificial Intelligence
- API: Application Programming Interface
- CSV: Comma-Separated Values
- CORS: Cross-Origin Resource Sharing
- GBR: Gradient Boosting Regressor
- LKR: Sri Lankan Rupees
- ML: Machine Learning
- UI: User Interface
- UX: User Experience
- REST: Representational State Transfer
- JSON: JavaScript Object Notation

## INTRODUCTION
University students often struggle to manage monthly finances because expenses vary across accommodation, food, transportation, study materials, utilities, and personal spending. Many students estimate their budgets informally, which can lead to overspending, poor savings habits, and financial stress. The Student Budget Optimizer was designed to address this issue by giving students a structured, AI-supported way to understand their spending patterns and receive realistic recommendations.

### Background & Literature Survey
Existing student budgeting systems and personal finance tools generally focus on manual expense tracking, generic budgeting templates, or broad financial advice. However, these systems often do not consider university-specific living conditions, district-based cost differences, or local spending habits. In the Sri Lankan context, student costs are strongly influenced by transport routes, family financial support, rental conditions, and diet-related food choices. Recent research and industry practice show that AI and ML can be used effectively for prediction, classification, and personalized recommendation in decision-support systems.

### Research Gap
Most available budgeting solutions are not localized for Sri Lankan university students and do not provide integrated prediction, risk assessment, and optimization in one workflow. They also rarely combine calculated real-world expenses with machine learning and AI-generated action plans.

### Research Problem
Sri Lankan university students lack a localized intelligent tool that can estimate realistic living expenses, detect financial risk, and generate actionable budget optimization guidance based on their academic and lifestyle profile.

### Research Objectives
The research objectives define what the Student Budget Optimizer aims to achieve within the Uni-Finder platform.

### Main Objective
To design and implement an AI-powered student budget optimization component that can estimate expenses, assess financial risk, and generate practical strategies to improve student savings and spending behavior.

### Specific Objectives
- To gather student financial and lifestyle inputs through a structured multi-step interface.
- To estimate monthly food and transport costs using Sri Lanka-specific datasets and budgeting rules.
- To predict budget patterns using trained machine learning models.
- To classify the user's financial risk level based on income and spending behavior.
- To generate personalized optimization recommendations and AI-supported action plans.
- To provide a printable final report for user review and discussion.

## METHODOLOGY

### Requirement Gathering and Analysis
Requirements were identified by focusing on student budgeting pain points such as inaccurate cost estimation, low savings awareness, and difficulty understanding where monthly expenses could be reduced. The analysis considered both user-facing needs and system-level processing needs.

### Project Requirements
The component required a front-end budget form, a backend analysis engine, access to pricing datasets, ML models for prediction and classification, and a mechanism to display and optionally save results.

### Functional Requirements
- Collect student academic, financial, food, transport, and additional expense data.
- Calculate estimated monthly food budget.
- Calculate estimated monthly transport budget.
- Generate complete monthly expense analysis.
- Predict financial budget patterns using ML.
- Classify the student into a financial risk category.
- Recommend optimized alternatives for reducing expenses.
- Generate AI-powered strategy steps for budget improvement.
- Allow printing of a full analysis report.

### Non-Functional Requirements
- Fast response time for analysis generation.
- Localized and understandable output for Sri Lankan students.
- Maintainability through modular service separation.
- Reusability of datasets and trained models.
- Scalability for multiple students using the service.
- Usability through a simple multi-step form and visual result sections.

### Software Requirements
- React for the frontend user interface
- Flask for the budget analysis microservice
- Express and MongoDB for persistence
- Python libraries such as pandas, joblib, and Flask-CORS
- Pretrained ML model files and CSV datasets

### Personal Requirements
The developer is expected to understand React component flow, REST API communication, Python backend logic, ML model integration, and domain knowledge related to student budgeting in Sri Lanka.

### Feasibility Study
The project is technically feasible because it uses available frameworks, accessible CSV datasets, and pre-trained models. It is operationally feasible because students can interact with the system using familiar form-based input. It is economically feasible because the main services rely on open-source technologies, and optional AI generation can be used only when needed.

### Research Domain
This work belongs to the domains of financial decision-support systems, educational technology, machine learning applications, and personalized recommendation systems.

### Generative AI Models
The component includes a generative AI stage to produce a step-by-step budget optimization strategy after the main analysis is completed. This stage turns structured financial data into human-readable actions and motivation.

### Large Language Models
Large Language Models are used to transform the financial summary, expense breakdown, risk information, and optimization targets into an understandable strategy. In this component, the AI strategy is generated through an LLM-based API call that produces category-wise actions, savings targets, and a final optimized budget view.

### Audio Synthesis
This heading does not directly apply to the Student Budget Optimizer. In this component, the matching concept is response synthesis in textual form rather than sound generation. Instead of producing audio output, the system synthesizes a structured financial action plan from analysis results.

### Response Classifier
The matching concept in this component is the financial risk classifier. It determines whether the student's financial condition indicates low risk or high risk based on processed input features and ML inference.

### Methodology
The implementation follows a layered methodology:
- Data collection through a multi-step React form
- Rule-based budget calculation for food and transport
- ML-based budget prediction and risk assessment
- Generation of optimized alternatives and savings targets
- LLM-based explanation and action-plan generation
- Presentation of results in a user-friendly dashboard and printable report

### Dataset and Data Structure Acquisition
The component uses structured CSV files and trained model files from the budget optimizer service. The main datasets include food prices, vegetable and fruit prices, transport costs, room rental records, academic calendar data, interest rates, and student survey data. The data is stored in CSV format and loaded by the Python service at runtime. Trained model files are stored as serialized `.pkl` files.

### Development & Implementation
The solution was implemented as a microservice-based architecture:
- React frontend for input collection and results presentation
- Flask budget service for calculations, ML prediction, and AI strategy generation
- Express backend for saving analysis results
- Model and reference data storage inside the budget optimizer service

### Audio Generation Component
This heading is not directly relevant to the budget optimizer. The closest equivalent is the AI strategy generation component, which creates detailed text-based recommendations instead of audio output.

### Classify Audio by using a Sound Profile
The corresponding concept in this component is classifying the student's financial condition by using a structured financial profile. Inputs such as income, rent, food habits, transport behavior, and expense breakdown are used to assess financial risk.

### Synthesize Generated Audio using the Dataset of Sample Sounds
The corresponding concept in this component is synthesizing recommendations using financial data and model outputs. Instead of sample sounds, the system uses expense calculations, risk classification, and optimization data to generate final advice and budget strategy text.

### Ling 6 Sound Generator
This heading has no direct equivalent in the budget optimizer domain. A matching replacement is the AI Budget Strategy Generator, which creates a detailed personalized improvement plan based on the user's financial state.

### Child Response Identifier
This can be matched with the Student Financial Response Identifier, where the system identifies whether the student is financially stable, at risk, or in need of immediate optimization guidance.

### Response Classifier
In the Student Budget Optimizer, the response classifier is the ML-based risk assessment module that predicts the probability of financial risk and attaches recommendations to the result.

### Clinician Web Interface
The matching concept in this component is the Student Budget Web Interface. It provides the user-facing dashboard for entering data, viewing analysis, examining optimized alternatives, generating AI strategy output, and printing a report.

### Testing
Testing includes:
- Input validation testing for form fields
- API testing for food, transport, prediction, and complete analysis endpoints
- UI testing for multi-step navigation and result rendering
- Verification of AI strategy generation and fallback behavior
- Manual testing of printing and result persistence

### Commercialization
The Student Budget Optimizer can be commercialized as part of a broader student support platform. It can be packaged with advanced analytics, premium guidance, and integrated financial advisory features.

### Target Audience
- Undergraduate students in Sri Lanka
- Private and state university students
- Students living away from home
- Parents supporting student finances
- Educational support platforms and advisors

### Subscription Plans
- Free Tier: Basic budget calculation and summary analysis
- Standard Tier: Full optimization guidance and printable reports
- Premium Tier: AI-generated personalized strategies and future financial planning features

### Marketplace
The component can be positioned inside the Uni-Finder platform marketplace as a student financial planning tool, and can also be bundled with scholarship, degree recommendation, and career guidance services.

## RESULTS & DISCUSSION

### Observing Therapy Sessions
This heading does not match the budget domain directly. The closest equivalent is observing student budgeting behavior through submitted inputs and generated results. The component allows analysis of how students allocate money across key categories and where common financial stress points appear.

### Generating Sounds According to the Child’s Progress
The corresponding concept is generating budget strategies according to the student's financial progress. Based on current expenses, savings rate, and optimization potential, the system produces progressively improved recommendations and target budgets.

### Results
The implemented component produces:
- A complete financial summary including total income, total expenses, monthly savings, and savings rate
- Auto-calculated food and transport budgets
- A machine learning-based budget prediction
- A financial risk assessment with probability score
- Optimized alternatives for reducing expenses
- An AI-powered step-by-step strategy for achieving a safer monthly budget
- A printable report for documentation and review

The results demonstrate that the component is not limited to expense display only; it acts as a decision-support tool that explains current financial status and suggests practical next steps.

## CONCLUSION
The Student Budget Optimizer successfully adapts AI and machine learning techniques to the problem of student financial planning in Sri Lanka. The component integrates localized cost calculation, budget prediction, financial risk classification, and personalized optimization strategy generation into a single workflow. By converting raw student inputs into meaningful, actionable guidance, the system helps users understand their financial condition and improve their budgeting behavior. Overall, this component is a practical and scalable contribution to the Uni-Finder platform and can be further expanded with stronger analytics, live financial data, and long-term financial planning capabilities.


source "/Users/shehansalitha/Desktop/research implementation/Uni-Finder/.venv/bin/activate"
cd budget_optimizer_service
python3 app.py

//kill
lsof -ti :5002 | xargs kill -9 2>/dev/null; echo "Port cleared"
