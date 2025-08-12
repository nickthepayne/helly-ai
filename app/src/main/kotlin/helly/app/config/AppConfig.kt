package helly.app.config

import helly.app.api.AskResponseDTO
import helly.app.application.*
import helly.app.domain.Feedback
import helly.app.domain.TeamMember
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import java.time.Instant
import java.util.UUID

@Configuration
class AppConfig {

    @Bean
    fun eventPublisher(): EventPublisher = NoopEventPublisher()

    @Bean
    fun entityResolutionService(): EntityResolutionService = SimpleEntityResolutionService()


    @Bean
    fun feedbackService(
        feedbackRepository: FeedbackRepository,
        eventPublisher: EventPublisher,
        entityResolutionService: EntityResolutionService,
        aiClient: AiClient
    ): FeedbackService = FeedbackService(feedbackRepository, eventPublisher, entityResolutionService, aiClient)


    @Bean
    fun restTemplate(): org.springframework.web.client.RestTemplate = org.springframework.web.client.RestTemplate()

    @Bean
    fun aiClient(): AiClient {
        val baseUrl = System.getenv("AI_BASE_URL") ?: "http://localhost:8001"
        return helly.app.infrastructure.ai.HttpAiClient(restTemplate(), baseUrl)
    }

    @Bean
    fun askService(aiClient: AiClient, entityResolutionService: EntityResolutionService): AskService =
        AskService(aiClient, entityResolutionService)
}


class NoopEventPublisher : EventPublisher {
    override fun publish(event: helly.app.domain.FeedbackCreated) { /* no-op */ }
}

class SimpleEntityResolutionService : EntityResolutionService {
    override fun resolveMember(content: String, hint: String?): String {
        // Extremely naive: expect a UUID in hint, otherwise look up a fake mapping by name initial.
        // For real usage, the /app would call /ai /resolve/member with candidates and decide.
        return hint ?: UUID.randomUUID().toString()
    }
}

class NoopAiClient : AiClient {
    override fun ask(text: String): AskResponseDTO = AskResponseDTO(
        answer = "Noop AI client: not implemented",
        citations = emptyList()
    )
    override fun ingestAll(teamMemberId: String, items: List<Feedback>) { /* no-op */ }
}

