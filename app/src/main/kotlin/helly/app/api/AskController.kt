package helly.app.api

import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/v1/ask")
class AskController {
    @PostMapping
    fun ask(@RequestBody body: AskDTO): AskResponseDTO {
        // Delegate to AiClient with person_hint
        throw UnsupportedOperationException("Not implemented in MVP scaffold")
    }
}

data class AskDTO(
    val question: String,
    val from: String?,
    val to: String?,
    val person_hint: String?
)

data class AskResponseDTO(
    val answer: String,
    val citations: List<FeedbackRef>?
)

data class FeedbackRef(
    val id: String,
    val created_at: String,
    val snippet: String
)

