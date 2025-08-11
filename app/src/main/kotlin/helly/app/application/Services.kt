package helly.app.application

import helly.app.domain.Feedback
import helly.app.domain.FeedbackCreated

class FeedbackService(
    private val feedbackRepository: FeedbackRepository,
    private val eventPublisher: EventPublisher,
    private val entityResolutionService: EntityResolutionService
) {
    fun addFeedback(content: String, createdAt: String?, personHint: String?): Feedback {
        // Resolve member id from content/hint
        throw UnsupportedOperationException("Design-only scaffold")
    }
}

class AskService(
    private val aiClient: AiClient,
    private val entityResolutionService: EntityResolutionService
) {
    fun ask(text: String) = aiClient.ask(text)
}

