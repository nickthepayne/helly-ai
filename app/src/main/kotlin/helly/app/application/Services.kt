package helly.app.application

import helly.app.domain.Feedback
import helly.app.domain.FeedbackCreated
import java.time.Instant
import java.util.UUID

class FeedbackService(
    private val feedbackRepository: FeedbackRepository,
    private val eventPublisher: EventPublisher,
    private val entityResolutionService: EntityResolutionService,
    private val aiClient: AiClient
) {
    fun addFeedback(content: String, createdAt: String?, personHint: String?): Feedback {
        val memberId = entityResolutionService.resolveMember(content, personHint)
        val feedback = Feedback(
            id = UUID.randomUUID().toString(),
            teamMemberId = memberId,
            content = content,
            createdAt = createdAt ?: Instant.now().toString()
        )
        feedbackRepository.create(feedback)
        eventPublisher.publish(FeedbackCreated(id = feedback.id, teamMemberId = memberId, createdAt = feedback.createdAt))
        // For MVP: call AI ingestion with just this item (full corpus sync later)
        aiClient.ingestAll(memberId, listOf(feedback))
        return feedback
    }
}

class AskService(
    private val aiClient: AiClient,
    private val entityResolutionService: EntityResolutionService
) {
    fun ask(text: String) = aiClient.ask(text)
}

