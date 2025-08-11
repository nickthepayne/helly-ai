package helly.app.application

import helly.app.api.AskResponseDTO
import helly.app.domain.FeedbackCreated
import helly.app.domain.Feedback
import helly.app.domain.TeamMember

interface TeamMemberRepository {
    fun create(member: TeamMember): TeamMember
    fun get(id: String): TeamMember?
    fun list(search: String?): List<TeamMember>
}

interface FeedbackRepository {
    fun create(feedback: Feedback): Feedback
    fun list(memberRef: String?, from: String?, to: String?): List<Feedback>
}

interface AiClient {
    fun ask(question: String, from: String?, to: String?, personHint: String?): AskResponseDTO
    fun ingestAll(teamMemberId: String, items: List<Feedback>)
}

interface EventPublisher {
    fun publish(event: FeedbackCreated)
}

interface EntityResolutionService {
    fun resolveMemberRef(content: String, hint: String?): String
}

