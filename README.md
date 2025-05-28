## AI Features

This application integrates with Ollama to provide several AI-powered features:

### Leave Request Status Decision
Provides AI-driven suggestions for leave request statuses (approved, rejected, needs discussion) based on team context. This is triggered via an admin-only batch processing API endpoint: `POST /leaves/prioritize-batch`. The AI's reasoning for its suggestion is stored with the leave request's updated status.

### Training Course Recommendation
Offers personalized training course recommendations for users. This is based on an analysis of the user's profile (role, start date), their Key Performance Indicator (KPI) results, completed past training, and the list of available courses in the system. Recommendations can include existing cataloged courses or suggest new course ideas. Accessed via `GET /users/{user_id}/ai-training-recommendations`.

### KPI Assessment
Provides AI-generated qualitative assessments and reasoning for an employee's KPI results. This is triggered via an admin-only batch processing API endpoint: `POST /kpis/assess-batch`. The AI's assessment and reasoning are stored alongside the KPI results.

## Configuration

### Ollama Integration
The AI features leverage a connection to an Ollama instance, which must be running and accessible to the application. The following environment variables are used to configure this integration:

-   `OLLAMA_API_URL`: Specifies the full URL for the Ollama API's generation endpoint.
    -   Defaults to: `http://localhost:11434/api/generate`
    -   Example: `OLLAMA_API_URL="http://my-ollama-server:11434/api/generate"`
-   `OLLAMA_DEFAULT_MODEL`: Defines the default Ollama model to be used for AI generation tasks if a specific model is not requested by the AI service.
    -   Defaults to: `mistral`
    -   Example: `OLLAMA_DEFAULT_MODEL="llama3"`
