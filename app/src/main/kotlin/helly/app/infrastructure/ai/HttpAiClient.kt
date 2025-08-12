package helly.app.infrastructure.ai

import com.fasterxml.jackson.annotation.JsonProperty
import helly.app.api.AskResponseDTO
import helly.app.api.FeedbackRef
import helly.app.application.AiClient
import helly.app.domain.Feedback
import org.springframework.web.client.RestTemplate

class HttpAiClient(
    private val restTemplate: RestTemplate,
    private val baseUrl: String
) : AiClient {

    override fun ask(text: String): AskResponseDTO {
        val req = QueryRequest(text = text)
        val resp = restTemplate.postForObject("$baseUrl/v1/query", req, AiQueryResponse::class.java)
        val citations = resp?.citations?.map { FeedbackRef(id = it.id, createdAt = it.createdAt, snippet = it.snippet) }
        return AskResponseDTO(answer = resp?.answer ?: "", citations = citations)
    }

    override fun ingestAll(teamMemberId: String, items: List<Feedback>) {
        val payload = IngestRequest(
            teamMemberRef = teamMemberId,
            items = items.map { AiFeedbackItem(id = it.id, content = it.content, createdAt = it.createdAt) },
            wipeExisting = false
        )
        restTemplate.postForLocation("$baseUrl/v1/ingest/member-corpus", payload)
    }
}

// ---- DTOs matching the AI service ----
private data class QueryRequest(
    val text: String,
    @JsonProperty("from_") val from: String? = null,
    val to: String? = null,
    @JsonProperty("person_hint") val personHint: String? = null
)

private data class AiQueryResponse(
    val answer: String,
    val citations: List<AiFeedbackRef>? = null
)

private data class AiFeedbackRef(
    val id: String,
    @JsonProperty("created_at") val createdAt: String,
    val snippet: String
)

private data class IngestRequest(
    @JsonProperty("team_member_ref") val teamMemberRef: String,
    val items: List<AiFeedbackItem>,
    @JsonProperty("from_") val from: String? = null,
    val to: String? = null,
    @JsonProperty("wipe_existing") val wipeExisting: Boolean = false
)

private data class AiFeedbackItem(
    val id: String,
    val content: String,
    @JsonProperty("created_at") val createdAt: String
)

