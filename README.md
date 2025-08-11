# helly-ai

## Running the services (MVP scaffold)

### /app (Kotlin Spring Boot)
Prereqs: Java 21

- cd app
- ./gradlew test
- ./gradlew bootRun

### /ai (Python FastAPI)
- cd ai
- make install  # installs via pip
- npm run dev   # runs uvicorn with reload on port 8001
- npm run test  # runs pytest
