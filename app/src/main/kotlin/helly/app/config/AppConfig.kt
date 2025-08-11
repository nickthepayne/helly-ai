package helly.app.config

import helly.app.api.AskResponseDTO
import helly.app.application.*
import helly.app.domain.Feedback
import helly.app.domain.TeamMember
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import java.time.Instant
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

@Configuration
class AppConfig {

    // In-memory repositories (MVP)
    @Bean
    fun teamMemberRepository(): TeamMemberRepository = InMemoryTeamMemberRepository()

    @Bean
    fun feedbackRepository(): FeedbackRepository = InMemoryFeedbackRepository()

    @Bean
    fun eventPublisher(): EventPublisher = NoopEventPublisher()

    @Bean
    fun entityResolutionService(): EntityResolutionService = SimpleEntityResolutionService()

    @Bean
    fun aiClient(): AiClient = NoopAiClient()

    @Bean
    fun feedbackService(
        feedbackRepository: FeedbackRepository,
        eventPublisher: EventPublisher,
        entityResolutionService: EntityResolutionService,
        aiClient: AiClient
    ): FeedbackService = FeedbackService(feedbackRepository, eventPublisher, entityResolutionService, aiClient)

    @Bean
    fun askService(aiClient: AiClient, entityResolutionService: EntityResolutionService): AskService =
        AskService(aiClient, entityResolutionService)
}

// Implementations
class InMemoryTeamMemberRepository : TeamMemberRepository {
    private val data = ConcurrentHashMap<String, TeamMember>()
    override fun create(member: TeamMember): TeamMember {
        data[member.id] = member
        return member
    }
    override fun get(id: String): TeamMember? = data[id]
    override fun list(search: String?): List<TeamMember> =
        data.values.filter { search.isNullOrBlank() || it.name.contains(search!!, ignoreCase = true) }
}

class InMemoryFeedbackRepository : FeedbackRepository {
    private val data = ConcurrentHashMap<String, Feedback>()
    override fun create(feedback: Feedback): Feedback {
        data[feedback.id] = feedback
        return feedback
    }
    override fun list(memberId: String?, from: String?, to: String?): List<Feedback> {
        val fromTs = from?.let { Instant.parse(it) }
        val toTs = to?.let { Instant.parse(it) }
        return data.values.filter { f ->
            (memberId == null || f.teamMemberId == memberId) &&
            (fromTs == null || Instant.parse(f.createdAt) >= fromTs) &&
            (toTs == null || Instant.parse(f.createdAt) <= toTs)
        }.sortedBy { it.createdAt }
    }
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

