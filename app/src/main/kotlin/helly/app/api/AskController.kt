package helly.app.api

import helly.app.application.AskService
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/v1/ask")
class AskController(private val service: AskService) {
    @PostMapping
    fun ask(@RequestBody body: AskDTO): AskResponseDTO {
        return service.ask(body.text)
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

