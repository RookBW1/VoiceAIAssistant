# Voice AI Support Assistant (E-commerce Returns & Service)

A highly responsive, local, and cost-effective voice-enabled intelligence engine designed to automate returns management and contextual order routing for enterprise e-commerce platforms. Built as a high-velocity prototype demonstrating modular design and technical resilience for the **Astrixx Evaluation**.

---

## Setup & Execution Instructions

### 1. Prerequisites & Environment Setup
Ensure you have Python 3.9 through Python 3.12 installed. Clone this repository, navigate to the directory, and initialize an isolated virtual environment:

```bash
# Navigate to workspace
cd VoiceAIAssistant

# Initialize and activate environment
python3 -m venv venv
source venv/Scripts/activate  # On Windows Git Bash: source venv/Scripts/activate


### 2. Dependency Installation
Install the required open-source and free-tier compliant library ecosystem:

```bash
pip install -r requirements.txt


###3. Environment Configuration
Create a .env file in the root directory to store your free Google AI Studio developer credentials:

code snippet
GEMINI_API_KEY=your_free_gemini_api_key_here

###4. Running the Architecture
The system is built as a microservice framework separating the processing core from the interface. Open two separate terminal windows with your virtual environment activated:

Terminal 1 (FastAPI Engine Backend - Port 8000):
uvicorn main:app --reload --port 8000

Terminal 2 (Streamlit GUI Interface - Port 8501):
streamlit run app.py


---

## ⚖️ Design Decisions & Trade-offs

**Strategic Selection of Gemini 2.5 Flash Engine**
We deliberately chose to implement the Gemini 2.5 Flash model over larger foundational models to optimize for First Token Latency (FTL). In interactive voice support applications, response velocity carries a significantly higher user experience weight than deep academic reasoning capabilities. While a larger model might offer marginal improvements in complex reasoning, the resulting network latency would break the natural cadence of a voice conversation. Gemini 2.5 Flash strikes the perfect balance by delivering near-instantaneous responses while maintaining accurate contextual comprehension.

**Decoupled Microservice Architecture**
The system is intentionally engineered with a strict separation of concerns, decoupling the FastAPI processing core from the Streamlit presentation interface. The primary trade-off here was a slightly higher initial setup complexity compared to building a single, monolithic script. However, this architecture ensures the system is enterprise-ready. By keeping the AI engine completely independent of the UI web surface, the core voice-processing backend can scale dynamically to serve a mobile application, a frontend web portal, or a traditional telephone IVR system in the future without modifying the underlying business logic.

**gTTS Core Integration for System Stability**
We integrated gTTS (Google Text-to-Speech) as our core synthesis engine, moving away from thread-bound operating system alternatives like pyttsx3. This choice traded away the ability to perform fine-grained, offline voice modulations in exchange for absolute runtime resilience. Because gTTS processes speech rendering as a lightweight, reliable I/O transaction that saves natively to an audio file, it prevents asynchronous thread deadlocks within FastAPI request worker threads. This ensures that the application runs stably across heterogeneous deployment machines during evaluation.

---

## Design Assumptions & Business Logic Guardrails
To address the open-ended nature of the problem, the following design constraints were established to guarantee execution predictability:

Temporal Anchoring: The "Current Operational Date" for evaluating policy timelines is strictly locked to June 1, 2026 (matching our transaction landscape).

Deterministic Return Window Calculations:

ORD123 delivered on 2026-05-20. Since June 1st is past the 7-day policy limit, the engine explicitly denies the return request via voice.

ORD125 delivered on 2026-05-10. Expired on 2026-05-17. Explicitly denied via local policy verification.

Audio Strategy: Bypassed complex browser WebSockets streaming in favor of file-upload and native browser recording components (.wav/.mp3). This design choice minimizes network jitter risks during evaluation and tracks pipeline latency deterministically.

Zero-Hallucination Constraints: The LLM's system prompt utilizes hard temperature clamping (0.2) and explicit negative constraints. If a client query falls outside the bounds of the provided data, the system flags a warm human handoff rather than inventing tracking states.

---


## Future Improvements & Scalability Moats
If scaled into an enterprise production cycle inside the Astrixx architecture, the platform would be hardened using these advanced engineering layers:

Vector Store Integration: Move static JSON context chunks into a high-performance vector database (e.g., Pinecone or Qdrant) to support thousands of dynamic institutional mutual fund rulebooks via true Semantic RAG pipelines.

Bi-directional WebSockets: Implement a streaming socket connection using local chunking frameworks to pipe raw mic audio frames to the backend asynchronously, enabling the AI to handle mid-sentence interruptions and achieve sub-second turnaround times.

---


## Roadblocks, Challenges, & Troubleshooting Log
Building a robust Voice-RAG pipeline under tight time constraints surfaced real-world engineering hurdles. Below is the explicit log of issues encountered and remediated during development:

Challenge 1: Subscription Gateways & Token Pricing Barriers

Roadblock: Initial pipeline blueprints relied on standard cloud vendor architectures (OpenAI Whisper + TTS). However, these require pre-paid billing profiles, creating friction for local evaluation execution and potential rate-limiting.

Remediation: Pivoted the architecture entirely to a hybrid local-open-source / free-tier paradigm. Replaced Whisper with the free SpeechRecognition pipeline, and integrated Google's highly generous free developer tier via Google AI Studio.

Challenge 2: Client SDK Deprecation (404 Not Found)
Error Message Encountered: google.genai.errors.ClientError: 404 NOT_FOUND. {'error': {'code': 404, 'message': 'models/gemini-1.5-flash is not found for API version v1beta...'}}

Root Cause Analysis: Google recently deprecated the legacy google-generativeai package, shifting backend routing channels to the brand-new google-genai native SDK. Legacy model strings failed string matching on the new API router gateway.

Remediation: Refactored services/assistant.py to leverage the modern from google import genai client framework and upgraded the underlying model asset to the flagship speed model: gemini-2.5-flash.

Challenge 3: Asynchronous Web Context Thread Blocking (HTTP 500 Error)
Error Message Encountered: "POST /api/process-voice-support HTTP/1.1" 500 Internal Server Error

Root Cause Analysis: Offline operating-system-level speech synthesis engines (like pyttsx3) require direct access to the host computer's main thread loop. When executed inside FastAPI's asynchronous request worker threads, it induced deadlocks, throwing generic 500 failures to the Streamlit layer.

Remediation: Abstracted the audio generation stage out of the local OS layer by introducing gTTS (Google Text-to-Speech). This moved file rendering to a reliable, lightweight I/O transaction that handles binary file tracking beautifully within web workers.