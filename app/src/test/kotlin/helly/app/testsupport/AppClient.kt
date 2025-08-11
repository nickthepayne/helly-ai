package helly.app.testsupport

import helly.app.api.AskResponseDTO
import helly.app.api.FeedbackDTO
import helly.app.api.TeamMemberDTO
import org.springframework.boot.test.web.client.TestRestTemplate

class AppClient(private val rest: TestRestTemplate, private val port: Int) {
    var lastMember: TeamMemberDTO? = null
        private set
    var lastFeedback: FeedbackDTO? = null
        private set
    var lastAsk: AskResponseDTO? = null
        private set

    fun createMember(
        name: String,
        role: String,
        relationshipToManager: String,
        startDate: String
    ): AppClient {
        val body = mapOf(
            "name" to name,
            "role" to role,
            "relationshipToManager" to relationshipToManager,
            "startDate" to startDate
        )
        val resp = rest.postJson<TeamMemberDTO>(port, "/v1/team-members", body)
        check(resp.statusCode.is2xxSuccessful) { "Failed to create member: ${resp.statusCode}" }
        lastMember = resp.body
        return this
    }

    fun addFeedback(
        content: String,
        personHint: String? = null,
        createdAt: String? = null
    ): AppClient {
        val hint = personHint ?: lastMember?.id
        val body = mapOf(
            "content" to content,
            "personHint" to hint,
            "createdAt" to createdAt
        ).filterValues { it != null }
        val resp = rest.postJson<FeedbackDTO>(port, "/v1/feedback", body)
        check(resp.statusCode.is2xxSuccessful) { "Failed to add feedback: ${resp.statusCode}" }
        lastFeedback = resp.body
        return this
    }

    fun ask(text: String): AppClient {
        val resp = rest.postJson<AskResponseDTO>(port, "/v1/ask", mapOf("text" to text))
        check(resp.statusCode.is2xxSuccessful) { "Failed to ask: ${resp.statusCode}" }
        lastAsk = resp.body
        return this
    }
}

