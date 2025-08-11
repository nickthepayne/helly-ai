package helly.app.api

import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/v1/ask")
class AskController {
    @PostMapping
    fun ask(@RequestBody body: AskDTO): AskResponseDTO {
        // For MVP: accept only free text; AI will resolve entities as needed
        throw UnsupportedOperationException("Not implemented in MVP scaffold")
    }
}

data class AskDTO(
    val text: String
)

data class AskResponseDTO(
    val answer: String,
    val citations: List<FeedbackRef>?
)

data class FeedbackRef(
    val id: String,
    val createdAt: String,
    val snippet: String
)

